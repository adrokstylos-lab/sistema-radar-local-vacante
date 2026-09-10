"""Endpoint de estadísticas agregadas."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.api.schemas import StatsOut
from backend.app.db.models import Business, Chain, Job, Scan

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsOut)
def stats(include_demo: bool = False, db: Session = Depends(get_db)):
    demo_filter = [] if include_demo else [Business.is_demo.is_(False)]
    job_demo = [] if include_demo else [Job.is_demo.is_(False)]

    base = select(Business).where(Business.merged_into_id.is_(None), *demo_filter)

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar() or 0

    by_cat_rows = db.execute(
        select(Business.primary_category, func.count())
        .where(Business.merged_into_id.is_(None), *demo_filter)
        .group_by(Business.primary_category)
    ).all()
    by_category = {c or "sin_categoria": n for c, n in by_cat_rows}

    total_jobs = db.execute(
        select(func.count()).select_from(Job).where(*job_demo)
    ).scalar() or 0

    jobs_by_cat_rows = db.execute(
        select(Job.title_category, func.count()).where(*job_demo).group_by(Job.title_category)
    ).all()
    jobs_by_category = {c or "sin_categoria": n for c, n in jobs_by_cat_rows}

    # Negocios con al menos una vacante (directa o de su cadena, mismo ámbito demo/real)
    businesses = db.execute(base).scalars().all()
    jobs = db.execute(select(Job).where(*job_demo)).scalars().all()
    chain_jobs = {j.chain_id for j in jobs if j.business_id is None and j.chain_id}
    direct_jobs = {j.business_id for j in jobs if j.business_id}
    with_jobs = sum(
        1 for b in businesses if b.id in direct_jobs or (b.chain_id and b.chain_id in chain_jobs)
    )

    chains = db.execute(
        select(func.count()).select_from(Chain).where(
            *( [] if include_demo else [Chain.is_demo.is_(False)] )
        )
    ).scalar() or 0

    last_scan = db.execute(select(func.max(Scan.finished_at))).scalar()

    return StatsOut(
        total_businesses=total,
        by_category=by_category,
        businesses_with_jobs=with_jobs,
        total_jobs=total_jobs,
        jobs_by_category=jobs_by_category,
        chains=chains,
        last_scan_at=last_scan,
    )
