"""Endpoints de vacantes."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.api.schemas import JobOut
from backend.app.api.service import job_to_out
from backend.app.db.models import Job

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    job_title: str | None = Query(None, description="title_category, p. ej. 'mesero'"),
    scope: str | None = None,
    status: str | None = None,
    business_id: int | None = None,
    chain_id: int | None = None,
    has_salary: bool | None = None,
    include_demo: bool = False,
    order_by: Literal["recent", "salary"] = "recent",
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = select(Job)
    if not include_demo:
        q = q.where(Job.is_demo.is_(False))
    if job_title:
        q = q.where(Job.title_category == job_title)
    if scope:
        q = q.where(Job.scope == scope)
    if status:
        q = q.where(Job.status == status)
    if business_id is not None:
        q = q.where(Job.business_id == business_id)
    if chain_id is not None:
        q = q.where(Job.chain_id == chain_id)
    if has_salary is True:
        q = q.where(Job.salary_min.isnot(None))
    if has_salary is False:
        q = q.where(Job.salary_min.is_(None))

    if order_by == "salary":
        q = q.order_by(Job.salary_max.desc().nullslast())
    else:
        q = q.order_by(Job.detected_at.desc().nullslast(), Job.id.desc())

    jobs = db.execute(q.limit(limit).offset(offset)).scalars().all()
    return [job_to_out(j) for j in jobs]


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    return job_to_out(job)
