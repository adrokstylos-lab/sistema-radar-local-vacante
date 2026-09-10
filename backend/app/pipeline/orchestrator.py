"""Orquestador de tareas programadas.

`run_task` envuelve cada tarea con: registro en task_runs (historial), manejo de
errores (rollback + estado 'error' sin dejar el sistema a medias) y logging.
Los reintentos de red viven en la capa HTTP (tenacity).
"""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import get_logger
from backend.app.core.zones import get_primary_zone_config, get_zone_center, upsert_zone
from backend.app.db.models import (
    Business,
    BusinessContact,
    BusinessHours,
    Job,
    TaskRun,
)
from backend.app.db.session import SessionLocal
from backend.app.pipeline.dedup import dedup_zone
from backend.app.pipeline.discovery import discover_zone
from backend.app.pipeline.enrich import enrich_all
from backend.app.pipeline.jobs import ingest_jobs

logger = get_logger("radar.orchestrator")

# Umbrales (días) para heurísticas de refresco/cierre
STALE_JOB_DAYS = 30
STALE_BUSINESS_DAYS = 90


# ----------------------------- Tareas ------------------------------------

def task_discovery_scan(session: Session) -> dict:
    """Descubre negocios nuevos en la zona prioritaria (OSM). No pisa el centro
    ya confirmado por geocoder si existe."""
    from backend.app.providers.openstreetmap.nominatim import NominatimGeocoder
    from backend.app.providers.openstreetmap.overpass import OverpassPlaceProvider

    cfg = get_primary_zone_config()
    zone = upsert_zone(session, cfg)  # crea si no existe (centro aprox de config)
    center = get_zone_center(session, zone)
    if center is None:
        query = ", ".join(p for p in (cfg["name"], cfg.get("municipality"), cfg.get("state")) if p)
        geo = NominatimGeocoder().geocode(query)
        if geo:
            zone = upsert_zone(session, cfg, center_lat=geo["lat"], center_lng=geo["lng"])
            center = (geo["lat"], geo["lng"])
        else:
            center = (cfg.get("center_lat"), cfg.get("center_lng"))
    session.commit()
    lat, lng = center
    return discover_zone(session, zone, OverpassPlaceProvider(), lat, lng, cfg.get("radius_m", 1800))


def task_business_refresh(session: Session) -> dict:
    """Actualiza datos existentes: enriquecimiento + deduplicación."""
    enrich = enrich_all(session)
    dedup = dedup_zone(session)
    return {"enrich": enrich, "dedup": dedup}


def task_job_scan(session: Session) -> dict:
    """Busca vacantes reales en Jooble para las franquicias (si hay key)."""
    if not settings.jooble_api_key:
        return {"skipped": "sin JOOBLE_API_KEY"}
    from backend.app.db.models import Chain
    from backend.app.providers.jobs.jooble import JoobleJobProvider

    cfg = get_primary_zone_config()
    location = f"{cfg.get('municipality', '')}, {cfg.get('state', '')}".strip(", ")
    chains = session.execute(
        select(Chain.name).where(Chain.is_demo.is_(False))
    ).scalars().all()
    if not chains:
        return {"skipped": "sin franquicias"}
    queries = [{"keywords": name, "location": location} for name in chains]
    mx_terms = ["cuautitlan", "izcalli", "estado de mexico", "edomex", "cdmx",
                "ciudad de mexico", "naucalpan", "tlalnepantla", "atizapan"]
    return ingest_jobs(session, JoobleJobProvider(), queries,
                       municipality=cfg.get("municipality", ""), demo=False,
                       allowed_location_terms=mx_terms)


def task_job_refresh(session: Session) -> dict:
    """Marca como 'vencida' las vacantes reales activas no verificadas hace mucho
    (heurística; la re-verificación real requeriría reconsultar la fuente)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=STALE_JOB_DAYS)
    result = session.execute(
        update(Job)
        .where(Job.is_demo.is_(False), Job.status == "activa", Job.last_verified_at < cutoff)
        .values(status="vencida")
    )
    session.commit()
    return {"marcadas_vencidas": result.rowcount, "umbral_dias": STALE_JOB_DAYS}


def task_closure_check(session: Session) -> dict:
    """Reporta negocios reales sin verificar hace mucho (candidatos a revisar
    cierre). No cambia el estado automáticamente (evita falsos cierres)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=STALE_BUSINESS_DAYS)
    stale = session.execute(
        select(Business.id).where(
            Business.is_demo.is_(False),
            Business.merged_into_id.is_(None),
            Business.last_verified_at < cutoff,
        )
    ).scalars().all()
    return {"candidatos_a_revisar": len(stale), "umbral_dias": STALE_BUSINESS_DAYS}


def task_data_quality(session: Session) -> dict:
    """Reporte de completitud de datos (negocios/vacantes reales)."""
    def count(stmt) -> int:
        return session.execute(stmt).scalar() or 0

    from sqlalchemy import func

    real = (Business.is_demo.is_(False), Business.merged_into_id.is_(None))
    total = count(select(func.count()).select_from(Business).where(*real))
    sin_categoria = count(select(func.count()).select_from(Business).where(*real, Business.primary_category.is_(None)))
    con_contacto = count(
        select(func.count(func.distinct(BusinessContact.business_id)))
        .select_from(BusinessContact).join(Business, Business.id == BusinessContact.business_id).where(*real)
    )
    con_horario = count(
        select(func.count(func.distinct(BusinessHours.business_id)))
        .select_from(BusinessHours).join(Business, Business.id == BusinessHours.business_id).where(*real)
    )
    jobs_sin_salario = count(
        select(func.count()).select_from(Job).where(Job.is_demo.is_(False), Job.salary_min.is_(None))
    )
    return {
        "negocios": total,
        "sin_categoria": sin_categoria,
        "sin_contacto": total - con_contacto,
        "sin_horario": total - con_horario,
        "vacantes_sin_salario": jobs_sin_salario,
    }


# Registro: nombre -> (función, frecuencia sugerida)
TASKS: dict[str, tuple[Callable[[Session], dict], str]] = {
    "discovery_scan": (task_discovery_scan, "semanal"),
    "business_refresh": (task_business_refresh, "semanal"),
    "job_scan": (task_job_scan, "semanal (límite Jooble 500/vida)"),
    "job_refresh": (task_job_refresh, "cada 3 días"),
    "closure_check": (task_closure_check, "mensual"),
    "data_quality": (task_data_quality, "semanal"),
}


def run_task(name: str) -> dict:
    """Ejecuta una tarea registrada con historial y manejo de errores."""
    if name not in TASKS:
        raise KeyError(f"Tarea desconocida: {name}. Disponibles: {', '.join(TASKS)}")
    fn, _freq = TASKS[name]

    session = SessionLocal()
    run = TaskRun(name=name, started_at=datetime.now(timezone.utc), status="running")
    session.add(run)
    session.commit()

    try:
        stats = fn(session)
        run.status = "done"
        run.stats = stats
        run.finished_at = datetime.now(timezone.utc)
        session.commit()
        logger.info("Tarea '%s' OK: %s", name, stats)
        return stats
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        run.status = "error"
        run.error = str(exc)
        run.finished_at = datetime.now(timezone.utc)
        session.commit()
        logger.error("Tarea '%s' FALLÓ: %s", name, exc)
        raise
    finally:
        session.close()
