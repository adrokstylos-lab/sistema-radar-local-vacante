"""Helpers compartidos por los routers de la API."""
from __future__ import annotations

from datetime import datetime

from backend.app.api.schemas import JobOut
from backend.app.db.models import BusinessHours, Job


def open_now(hours: list[BusinessHours], now: datetime | None = None) -> bool | None:
    """True/False si hay horario para hoy; None si no hay información (no se inventa)."""
    if not hours:
        return None
    now = now or datetime.now()
    wd = now.weekday()  # 0=lunes
    t = now.time()
    todays = [h for h in hours if h.day_of_week == wd and h.open_time and h.close_time]
    if not todays:
        return False
    return any(h.open_time <= t <= h.close_time for h in todays)


def job_matches_business(job: Job, business_id: int, chain_id: int | None, is_demo: bool) -> bool:
    """Una vacante corresponde a un negocio si está ligada directamente, o si es
    de su cadena sin sucursal resuelta. Respeta la separación demo/real."""
    if job.is_demo is not is_demo:
        return False
    if job.business_id == business_id:
        return True
    return job.business_id is None and chain_id is not None and job.chain_id == chain_id


def job_to_out(job: Job) -> JobOut:
    return JobOut(
        id=job.id,
        title=job.title,
        title_category=job.title_category,
        description=job.description,
        scope=job.scope,
        status=job.status,
        confidence=job.confidence,
        salary_min=float(job.salary_min) if job.salary_min is not None else None,
        salary_max=float(job.salary_max) if job.salary_max is not None else None,
        currency=job.currency,
        salary_period=job.salary_period,
        modality=job.modality,
        address=job.address,
        source=job.source,
        source_url=job.source_url,
        detected_at=job.detected_at,
        posted_at=job.posted_at,
        business_id=job.business_id,
        chain_id=job.chain_id,
        is_demo=job.is_demo,
    )
