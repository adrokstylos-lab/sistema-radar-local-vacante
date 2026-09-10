"""Pipeline de descubrimiento: ejecuta un proveedor de lugares sobre una zona y
guarda los negocios encontrados (datos reales), con registro en scans y
source_requests. Evita duplicados por provider_place_id (dedup completa: Fase 5).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.logging import get_logger
from backend.app.db.models import (
    Business,
    BusinessContact,
    BusinessLocation,
    BusinessSource,
    GeographicZone,
    Scan,
    SourceRequest,
)
from backend.app.pipeline.normalize import normalize_name
from backend.app.providers.base import PlaceProvider

logger = get_logger("radar.discovery")

# Tags OSM -> tipo de contacto interno.
CONTACT_TAGS = {
    "phone": "telefono",
    "contact:phone": "telefono",
    "contact:mobile": "telefono",
    "contact:whatsapp": "whatsapp",
    "whatsapp": "whatsapp",
    "website": "web",
    "contact:website": "web",
    "url": "web",
    "email": "email",
    "contact:email": "email",
    "contact:facebook": "facebook",
    "contact:instagram": "instagram",
}


def _compose_address(tags: dict[str, str]) -> str | None:
    parts = [
        " ".join(p for p in (tags.get("addr:street"), tags.get("addr:housenumber")) if p),
        tags.get("addr:suburb") or tags.get("addr:neighbourhood"),
        tags.get("addr:city"),
        tags.get("addr:postcode"),
    ]
    parts = [p for p in parts if p]
    return ", ".join(parts) if parts else None


def _build_business(record: dict[str, Any], now: datetime) -> Business:
    tags = record["tags"]
    business = Business(
        normalized_name=normalize_name(record["name"]),
        display_name=record["name"],
        primary_category=record["category"],
        status="desconocido",  # OSM no confirma abierto/cerrado de forma fiable
        confidence="probable",
        last_verified_at=now,
        verification_source="openstreetmap",
        is_demo=False,
    )
    business.locations.append(
        BusinessLocation(
            full_address=_compose_address(tags),
            colonia=tags.get("addr:suburb") or tags.get("addr:neighbourhood"),
            municipality=tags.get("addr:city"),
            postal_code=tags.get("addr:postcode"),
            country="México",
            geog=WKTElement(f"POINT({record['lng']} {record['lat']})", srid=4326),
            provider="openstreetmap",
            provider_place_id=record["provider_place_id"],
        )
    )
    # Contactos (deduplicados por tipo+valor dentro del negocio)
    seen: set[tuple[str, str]] = set()
    for tag, ctype in CONTACT_TAGS.items():
        value = tags.get(tag)
        if value and (ctype, value) not in seen:
            seen.add((ctype, value))
            business.contacts.append(
                BusinessContact(type=ctype, value=value, source="openstreetmap", confidence="probable")
            )
    business.sources.append(
        BusinessSource(
            provider="openstreetmap",
            provider_place_id=record["provider_place_id"],
            raw=tags,
            fetched_at=now,
        )
    )
    return business


def discover_zone(
    session: Session,
    zone: GeographicZone,
    provider: PlaceProvider,
    center_lat: float,
    center_lng: float,
    radius_m: int,
) -> dict[str, int]:
    now = datetime.now(timezone.utc)
    scan = Scan(
        zone_id=zone.id,
        provider=provider.name,
        strategy="radius",
        area_covered={"center_lat": center_lat, "center_lng": center_lng, "radius_m": radius_m},
        started_at=now,
        status="running",
    )
    session.add(scan)
    session.flush()

    created = skipped = 0
    try:
        records = provider.search_places(lat=center_lat, lng=center_lng, radius_m=radius_m)

        # IDs ya presentes de este proveedor -> evitar duplicados en re-scans.
        existing = set(
            session.execute(
                select(BusinessSource.provider_place_id).where(
                    BusinessSource.provider == provider.name
                )
            ).scalars()
        )
        for rec in records:
            if rec["provider_place_id"] in existing:
                skipped += 1
                continue
            session.add(_build_business(rec, now))
            existing.add(rec["provider_place_id"])
            created += 1

        scan.results_count = len(records)
        scan.finished_at = datetime.now(timezone.utc)
        scan.status = "done"
        _log_request(session, provider, ok=True, results=len(records))
    except Exception as exc:  # noqa: BLE001
        scan.status = "error"
        scan.errors = {"message": str(exc)}
        scan.finished_at = datetime.now(timezone.utc)
        _log_request(session, provider, ok=False, error=str(exc))
        session.commit()
        logger.error("Descubrimiento falló: %s", exc)
        raise

    session.commit()
    stats = {"encontrados": len(records), "creados": created, "omitidos_duplicados": skipped}
    logger.info("Descubrimiento OK: %s", stats)
    return stats


def discover_grid(
    session: Session,
    zone: GeographicZone,
    provider: PlaceProvider,
    cells: list,
    skip_recent_days: int = 7,
) -> dict[str, int]:
    """Descubre negocios recorriendo un grid de celdas. Registra una fila en
    `scans` por celda (cobertura) y omite celdas escaneadas hace poco (evita
    consultas redundantes y costo)."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=skip_recent_days)
    totals = {"celdas": 0, "celdas_omitidas": 0, "encontrados": 0,
              "creados": 0, "omitidos_duplicados": 0}

    existing = set(
        session.execute(
            select(BusinessSource.provider_place_id).where(BusinessSource.provider == provider.name)
        ).scalars()
    )

    for cell in cells:
        totals["celdas"] += 1
        gh = cell.geohash

        recent = session.execute(
            select(Scan.id).where(
                Scan.strategy == "grid",
                Scan.status == "done",
                Scan.finished_at > cutoff,
                Scan.area_covered["geohash"].astext == gh,
            )
        ).first()
        if recent:
            totals["celdas_omitidas"] += 1
            continue

        scan = Scan(
            zone_id=zone.id, provider=provider.name, strategy="grid",
            area_covered={"geohash": gh, "center_lat": cell.center_lat,
                          "center_lng": cell.center_lng, "radius_m": cell.radius_m,
                          "bbox": list(cell.bbox)},
            started_at=datetime.now(timezone.utc), status="running",
        )
        session.add(scan)
        session.flush()
        try:
            records = provider.search_places(
                lat=cell.center_lat, lng=cell.center_lng, radius_m=cell.radius_m
            )
            for rec in records:
                if rec["provider_place_id"] in existing:
                    totals["omitidos_duplicados"] += 1
                    continue
                session.add(_build_business(rec, now))
                existing.add(rec["provider_place_id"])
                totals["creados"] += 1
            totals["encontrados"] += len(records)
            scan.results_count = len(records)
            scan.status = "done"
            scan.finished_at = datetime.now(timezone.utc)
            _log_request(session, provider, ok=True, results=len(records))
            session.commit()
        except Exception as exc:  # noqa: BLE001  (una celda falla, el grid continúa)
            session.rollback()
            scan = session.get(Scan, scan.id)
            if scan:
                scan.status = "error"
                scan.errors = {"message": str(exc)}
                scan.finished_at = datetime.now(timezone.utc)
                session.commit()
            logger.error("Celda %s falló: %s", gh, exc)

    logger.info("Descubrimiento grid: %s", totals)
    return totals


def _log_request(session: Session, provider: PlaceProvider, *, ok: bool,
                 results: int | None = None, error: str | None = None) -> None:
    meta = getattr(provider, "last_result", None)
    session.add(
        SourceRequest(
            provider=provider.name,
            endpoint=getattr(meta, "url", None),
            response_cached=False,
            status_code=getattr(meta, "status_code", None),
            latency_ms=getattr(meta, "latency_ms", None),
            results_count=results,
            error=error,
        )
    )
