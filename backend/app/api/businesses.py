"""Endpoints de negocios."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2 import Geometry
from sqlalchemy import and_, cast, func, literal, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.api.deps import get_db
from backend.app.api.schemas import (
    BusinessDetail,
    BusinessListItem,
    ContactOut,
    HoursOut,
)
from backend.app.api.service import job_matches_business, job_to_out, open_now
from backend.app.db.models import Business, BusinessLocation, Job

router = APIRouter(tags=["businesses"])

_ACTIVE = ("activa", "posible")


def _candidate_rows(db, *, lat, lng, radius, category, municipality, min_rating, include_demo):
    lat_e = func.ST_Y(cast(BusinessLocation.geog, Geometry)).label("lat")
    lng_e = func.ST_X(cast(BusinessLocation.geog, Geometry)).label("lng")
    point = func.ST_GeogFromText(f"SRID=4326;POINT({lng} {lat})") if lat is not None and lng is not None else None
    dist_e = (func.ST_Distance(BusinessLocation.geog, point) if point is not None else literal(None)).label("dist")

    q = (
        select(Business.id.label("bid"), lat_e, lng_e, dist_e)
        .join(BusinessLocation, BusinessLocation.business_id == Business.id)
        .where(Business.merged_into_id.is_(None))
    )
    if not include_demo:
        q = q.where(Business.is_demo.is_(False))
    if category:
        q = q.where(Business.primary_category == category)
    if municipality:
        q = q.where(BusinessLocation.municipality.ilike(f"%{municipality}%"))
    if min_rating is not None:
        q = q.where(Business.rating >= min_rating)
    if point is not None:
        q = q.where(func.ST_DWithin(BusinessLocation.geog, point, radius))
        q = q.distinct(Business.id).order_by(Business.id, func.ST_Distance(BusinessLocation.geog, point))
    else:
        q = q.distinct(Business.id).order_by(Business.id)
    return db.execute(q).all()


@router.get("/businesses", response_model=list[BusinessListItem])
def list_businesses(
    latitude: float | None = None,
    longitude: float | None = None,
    radius: int = Query(2000, ge=1, le=50000, description="metros; requiere lat/lng"),
    category: str | None = None,
    municipality: str | None = None,
    has_jobs: bool | None = None,
    job_title: str | None = Query(None, description="title_category, p. ej. 'mesero'"),
    open_now_only: bool = Query(False, alias="open_now"),
    min_rating: float | None = Query(None, ge=0, le=5),
    include_demo: bool = False,
    order_by: Literal["distance", "rating", "name", "recent"] = "distance",
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = _candidate_rows(
        db, lat=latitude, lng=longitude, radius=radius, category=category,
        municipality=municipality, min_rating=min_rating, include_demo=include_demo,
    )
    if not rows:
        return []
    geo = {r.bid: (r.lat, r.lng, r.dist) for r in rows}
    ids = list(geo)

    businesses = db.execute(
        select(Business)
        .where(Business.id.in_(ids))
        .options(selectinload(Business.hours), selectinload(Business.chain))
    ).scalars().all()

    chain_ids = {b.chain_id for b in businesses if b.chain_id}
    jobs = db.execute(
        select(Job).where(
            or_(Job.business_id.in_(ids),
                and_(Job.business_id.is_(None), Job.chain_id.in_(chain_ids or {-1})))
        )
    ).scalars().all()

    items: list[BusinessListItem] = []
    for b in businesses:
        lat_v, lng_v, dist_v = geo[b.id]
        b_jobs = [j for j in jobs if job_matches_business(j, b.id, b.chain_id, b.is_demo)]
        active = [j for j in b_jobs if j.status in _ACTIVE]
        is_open = open_now(b.hours)

        if has_jobs is True and not b_jobs:
            continue
        if has_jobs is False and b_jobs:
            continue
        if job_title and not any(j.title_category == job_title for j in b_jobs):
            continue
        if open_now_only and is_open is not True:
            continue

        items.append(BusinessListItem(
            id=b.id, display_name=b.display_name, primary_category=b.primary_category,
            food_type=b.food_type, rating=b.rating, reviews_count=b.reviews_count,
            status=b.status, municipality=None, lat=lat_v, lng=lng_v,
            distance_m=round(dist_v, 1) if dist_v is not None else None,
            has_jobs=bool(b_jobs), active_jobs_count=len(active), open_now=is_open,
            last_verified_at=b.last_verified_at, is_demo=b.is_demo,
        ))

    reverse = order_by in ("rating", "recent")
    keymap = {
        "distance": lambda i: (i.distance_m is None, i.distance_m or 0.0),
        "rating": lambda i: i.rating or 0.0,
        "name": lambda i: i.display_name.lower(),
        "recent": lambda i: i.last_verified_at or __import__("datetime").datetime.min,
    }
    items.sort(key=keymap[order_by], reverse=reverse)
    return items[offset: offset + limit]


@router.get("/businesses/{business_id}", response_model=BusinessDetail)
def get_business(business_id: int, db: Session = Depends(get_db)):
    b = db.execute(
        select(Business)
        .where(Business.id == business_id)
        .options(
            selectinload(Business.locations), selectinload(Business.hours),
            selectinload(Business.contacts), selectinload(Business.sources),
            selectinload(Business.chain),
        )
    ).scalar_one_or_none()
    if b is None:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")

    loc = b.locations[0] if b.locations else None
    lat_v = lng_v = None
    if loc is not None:
        coords = db.execute(
            select(func.ST_Y(cast(BusinessLocation.geog, Geometry)),
                   func.ST_X(cast(BusinessLocation.geog, Geometry)))
            .where(BusinessLocation.id == loc.id)
        ).first()
        if coords:
            lat_v, lng_v = coords[0], coords[1]

    jobs = db.execute(
        select(Job).where(
            or_(Job.business_id == b.id,
                and_(Job.business_id.is_(None),
                     Job.chain_id == (b.chain_id if b.chain_id else -1)))
        )
    ).scalars().all()
    b_jobs = [j for j in jobs if job_matches_business(j, b.id, b.chain_id, b.is_demo)]
    active = [j for j in b_jobs if j.status in _ACTIVE]

    return BusinessDetail(
        id=b.id, display_name=b.display_name, primary_category=b.primary_category,
        food_type=b.food_type, rating=b.rating, reviews_count=b.reviews_count,
        status=b.status, municipality=loc.municipality if loc else None,
        lat=lat_v, lng=lng_v, distance_m=None,
        has_jobs=bool(b_jobs), active_jobs_count=len(active), open_now=open_now(b.hours),
        last_verified_at=b.last_verified_at, is_demo=b.is_demo,
        secondary_categories=b.secondary_categories, description=b.description,
        services=b.services, price_range=b.price_range, confidence=b.confidence,
        chain_id=b.chain_id, chain_name=b.chain.name if b.chain else None,
        full_address=loc.full_address if loc else None,
        postal_code=loc.postal_code if loc else None,
        contacts=[ContactOut(type=c.type, value=c.value, source=c.source, confidence=c.confidence) for c in b.contacts],
        hours=[HoursOut(day_of_week=h.day_of_week, open_time=h.open_time, close_time=h.close_time,
                        source=h.source, confidence=h.confidence) for h in sorted(b.hours, key=lambda x: x.day_of_week)],
        jobs=[job_to_out(j) for j in b_jobs],
        sources=sorted({s.provider for s in b.sources}),
        updated_at=b.updated_at,
    )
