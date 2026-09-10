"""Negocios y sus datos asociados (ubicación, horarios, contacto, fuentes, historial)."""
from __future__ import annotations

from datetime import datetime, time

from geoalchemy2 import Geography
from geoalchemy2.elements import WKBElement
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.db.mixins import IdMixin, TimestampMixin


class Chain(IdMixin, TimestampMixin, Base):
    """Cadena o franquicia (McDonald's, Starbucks...)."""

    __tablename__ = "chains"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    careers_url: Mapped[str | None] = mapped_column(Text)
    ats_type: Mapped[str | None] = mapped_column(String(50))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    businesses: Mapped[list[Business]] = relationship(back_populates="chain")


class Business(IdMixin, TimestampMixin, Base):
    __tablename__ = "businesses"

    normalized_name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(300), nullable=False)
    primary_category: Mapped[str | None] = mapped_column(String(100), index=True)
    secondary_categories: Mapped[list | None] = mapped_column(JSONB)
    description: Mapped[str | None] = mapped_column(Text)

    chain_id: Mapped[int | None] = mapped_column(
        ForeignKey("chains.id", ondelete="SET NULL"), index=True
    )
    # Si no es NULL, este negocio fue fusionado como duplicado dentro de otro
    # (canónico). Permite fusiones reversibles y sin pérdida de datos.
    merged_into_id: Mapped[int | None] = mapped_column(
        ForeignKey("businesses.id", ondelete="SET NULL"), index=True
    )

    # Información comercial (flexible)
    food_type: Mapped[str | None] = mapped_column(String(150))
    services: Mapped[dict | None] = mapped_column(JSONB)  # dine_in, takeout, delivery, uber_eats...
    price_range: Mapped[str | None] = mapped_column(String(20))
    rating: Mapped[float | None] = mapped_column(Float)
    reviews_count: Mapped[int | None] = mapped_column(Integer)
    popularity: Mapped[float | None] = mapped_column(Float)

    # Estado del negocio (ver constants.BUSINESS_STATUS)
    status: Mapped[str] = mapped_column(String(30), default="desconocido", nullable=False)
    confidence: Mapped[str | None] = mapped_column(String(20))
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_source: Mapped[str | None] = mapped_column(String(100))

    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    chain: Mapped[Chain | None] = relationship(back_populates="businesses")
    locations: Mapped[list[BusinessLocation]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    hours: Mapped[list[BusinessHours]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    contacts: Mapped[list[BusinessContact]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    sources: Mapped[list[BusinessSource]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )


class BusinessLocation(IdMixin, TimestampMixin, Base):
    __tablename__ = "business_locations"

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    full_address: Mapped[str | None] = mapped_column(Text)
    colonia: Mapped[str | None] = mapped_column(String(200))
    municipality: Mapped[str | None] = mapped_column(String(200))
    state: Mapped[str | None] = mapped_column(String(200))
    postal_code: Mapped[str | None] = mapped_column(String(10))
    country: Mapped[str | None] = mapped_column(String(100))
    geog: Mapped[WKBElement | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    map_url: Mapped[str | None] = mapped_column(Text)
    provider: Mapped[str | None] = mapped_column(String(50))
    provider_place_id: Mapped[str | None] = mapped_column(String(200), index=True)

    business: Mapped[Business] = relationship(back_populates="locations")


class BusinessHours(IdMixin, TimestampMixin, Base):
    __tablename__ = "business_hours"

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=lunes ... 6=domingo
    open_time: Mapped[time | None] = mapped_column(Time)
    close_time: Mapped[time | None] = mapped_column(Time)
    source: Mapped[str | None] = mapped_column(String(100))
    confidence: Mapped[str | None] = mapped_column(String(20))

    business: Mapped[Business] = relationship(back_populates="hours")


class BusinessContact(IdMixin, TimestampMixin, Base):
    __tablename__ = "business_contacts"

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # ver constants.CONTACT_TYPES
    value: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(100))
    confidence: Mapped[str | None] = mapped_column(String(20))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    business: Mapped[Business] = relationship(back_populates="contacts")


class BusinessSource(IdMixin, TimestampMixin, Base):
    """De qué proveedor/fuente se obtuvo el negocio."""

    __tablename__ = "business_sources"
    __table_args__ = (
        UniqueConstraint("provider", "provider_place_id", name="uq_source_provider_place"),
    )

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_place_id: Mapped[str | None] = mapped_column(String(200))
    raw: Mapped[dict | None] = mapped_column(JSONB)
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    business: Mapped[Business] = relationship(back_populates="sources")


class BusinessSnapshot(IdMixin, TimestampMixin, Base):
    """Historial de cambios de un negocio (antes/después)."""

    __tablename__ = "business_snapshots"

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    diff: Mapped[dict | None] = mapped_column(JSONB)
