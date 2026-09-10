"""Vacantes y su historial/fuentes."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.db.mixins import IdMixin, TimestampMixin


class Job(IdMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    business_id: Mapped[int | None] = mapped_column(
        ForeignKey("businesses.id", ondelete="SET NULL"), index=True
    )
    chain_id: Mapped[int | None] = mapped_column(
        ForeignKey("chains.id", ondelete="SET NULL"), index=True
    )

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    title_category: Mapped[str | None] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(Text)

    salary_min: Mapped[float | None] = mapped_column(Numeric(12, 2))
    salary_max: Mapped[float | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str | None] = mapped_column(String(3))
    salary_period: Mapped[str | None] = mapped_column(String(20))  # hora/día/semana/mes/año

    schedule: Mapped[str | None] = mapped_column(String(150))
    shift: Mapped[str | None] = mapped_column(String(50))
    requirements: Mapped[dict | None] = mapped_column(JSONB)
    experience: Mapped[str | None] = mapped_column(String(150))
    education: Mapped[str | None] = mapped_column(String(150))
    address: Mapped[str | None] = mapped_column(Text)
    modality: Mapped[str | None] = mapped_column(String(50))  # presencial/híbrido/remoto

    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    detected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    source: Mapped[str | None] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(Text)
    contact: Mapped[dict | None] = mapped_column(JSONB)

    status: Mapped[str] = mapped_column(String(20), default="desconocido", nullable=False)
    scope: Mapped[str] = mapped_column(String(30), default="desconocido", nullable=False)
    confidence: Mapped[str | None] = mapped_column(String(20))

    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    sources: Mapped[list[JobSource]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class JobSource(IdMixin, TimestampMixin, Base):
    __tablename__ = "job_sources"

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    raw: Mapped[dict | None] = mapped_column(JSONB)
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    job: Mapped[Job] = relationship(back_populates="sources")


class JobSnapshot(IdMixin, TimestampMixin, Base):
    """Historial de la vacante (apareció / cambió / desapareció)."""

    __tablename__ = "job_snapshots"

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
