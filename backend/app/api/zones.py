"""Endpoints de zonas geográficas."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from geoalchemy2 import Geometry
from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.api.schemas import ZoneOut
from backend.app.db.models import GeographicZone

router = APIRouter(tags=["zones"])


@router.get("/zones", response_model=list[ZoneOut])
def list_zones(include_demo: bool = False, db: Session = Depends(get_db)):
    lat_e = func.ST_Y(cast(GeographicZone.center, Geometry)).label("lat")
    lng_e = func.ST_X(cast(GeographicZone.center, Geometry)).label("lng")
    q = select(GeographicZone, lat_e, lng_e).order_by(GeographicZone.priority.nullslast())
    if not include_demo:
        q = q.where(GeographicZone.is_demo.is_(False))
    out = []
    for z, lat_v, lng_v in db.execute(q).all():
        out.append(ZoneOut(
            id=z.id, name=z.name, municipality=z.municipality, state=z.state,
            country=z.country, postal_code=z.postal_code, priority=z.priority,
            strategy=z.strategy, radius_m=z.radius_m, lat=lat_v, lng=lng_v,
            is_active=z.is_active, is_demo=z.is_demo,
        ))
    return out
