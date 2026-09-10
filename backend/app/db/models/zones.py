"""Zonas geográficas donde se buscan negocios."""
from __future__ import annotations

from geoalchemy2 import Geography
from geoalchemy2.elements import WKBElement
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.db.mixins import IdMixin, TimestampMixin


class GeographicZone(IdMixin, TimestampMixin, Base):
    __tablename__ = "geographic_zones"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    municipality: Mapped[str | None] = mapped_column(String(200))
    state: Mapped[str | None] = mapped_column(String(200))
    country: Mapped[str | None] = mapped_column(String(100))
    postal_code: Mapped[str | None] = mapped_column(String(10))

    priority: Mapped[int | None] = mapped_column(Integer)
    strategy: Mapped[str] = mapped_column(String(20), default="radius", nullable=False)

    center: Mapped[WKBElement | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    radius_m: Mapped[int | None] = mapped_column(Integer)
    polygon: Mapped[WKBElement | None] = mapped_column(
        Geography(geometry_type="POLYGON", srid=4326)
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
