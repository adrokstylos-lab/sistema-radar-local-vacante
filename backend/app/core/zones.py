"""Carga de zonas desde config/zones.yaml y upsert a la tabla geographic_zones."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session

from backend.app.db.models import GeographicZone

CONFIG_PATH = Path("config/zones.yaml")


def load_zone_configs(path: Path = CONFIG_PATH) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("zones", [])


def get_primary_zone_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    zones = [z for z in load_zone_configs(path) if z.get("is_active", True)]
    if not zones:
        raise ValueError("No hay zonas activas en config/zones.yaml")
    return min(zones, key=lambda z: z.get("priority", 999))


def upsert_zone(
    session: Session,
    cfg: dict[str, Any],
    center_lat: float | None = None,
    center_lng: float | None = None,
) -> GeographicZone:
    """Crea o actualiza la zona (datos reales, is_demo=False)."""
    lat = center_lat if center_lat is not None else cfg.get("center_lat")
    lng = center_lng if center_lng is not None else cfg.get("center_lng")
    center = WKTElement(f"POINT({lng} {lat})", srid=4326) if lat and lng else None

    stmt = select(GeographicZone).where(
        GeographicZone.name == cfg["name"],
        GeographicZone.municipality == cfg.get("municipality"),
        GeographicZone.is_demo.is_(False),
    )
    zone = session.execute(stmt).scalar_one_or_none()
    if zone is None:
        zone = GeographicZone(name=cfg["name"], is_demo=False)
        session.add(zone)

    zone.municipality = cfg.get("municipality")
    zone.state = cfg.get("state")
    zone.country = cfg.get("country")
    zone.postal_code = cfg.get("postal_code")
    zone.priority = cfg.get("priority")
    zone.strategy = cfg.get("strategy", "radius")
    zone.radius_m = cfg.get("radius_m")
    zone.is_active = cfg.get("is_active", True)
    if center is not None:
        zone.center = center

    session.flush()
    return zone


def get_zone_center(session: Session, zone: GeographicZone) -> tuple[float, float] | None:
    """Devuelve (lat, lng) del centro de la zona, o None si no tiene."""
    row = session.execute(
        select(
            func.ST_Y(cast(GeographicZone.center, Geometry)),
            func.ST_X(cast(GeographicZone.center, Geometry)),
        ).where(GeographicZone.id == zone.id, GeographicZone.center.isnot(None))
    ).first()
    if not row or row[0] is None:
        return None
    return float(row[0]), float(row[1])
