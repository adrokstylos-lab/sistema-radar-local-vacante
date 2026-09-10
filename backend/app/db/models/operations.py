"""Tablas operativas: escaneos, registro de consultas a APIs y log de deduplicación."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base
from backend.app.db.mixins import IdMixin, TimestampMixin


class Scan(IdMixin, TimestampMixin, Base):
    """Ejecución de una búsqueda geográfica."""

    __tablename__ = "scans"

    zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("geographic_zones.id", ondelete="SET NULL"), index=True
    )
    provider: Mapped[str | None] = mapped_column(String(50))
    strategy: Mapped[str | None] = mapped_column(String(20))  # radius/grid/polygon
    area_covered: Mapped[dict | None] = mapped_column(JSONB)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    results_count: Mapped[int | None] = mapped_column(Integer)
    errors: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str | None] = mapped_column(String(30))


class SourceRequest(IdMixin, TimestampMixin, Base):
    """Registro de cada consulta externa: costo, caché y observabilidad."""

    __tablename__ = "source_requests"

    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    endpoint: Mapped[str | None] = mapped_column(String(200))
    request_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    response_cached: Mapped[bool | None] = mapped_column()
    cost_estimate: Mapped[float | None] = mapped_column(Numeric(10, 4))
    status_code: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    results_count: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)


class TaskRun(IdMixin, TimestampMixin, Base):
    """Historial de ejecuciones de tareas programadas (observabilidad)."""

    __tablename__ = "task_runs"

    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)
    stats: Mapped[dict | None] = mapped_column(JSONB)
    error: Mapped[str | None] = mapped_column(Text)


class MatchLog(IdMixin, TimestampMixin, Base):
    """Trazabilidad de decisiones de deduplicación (nada dudoso se fusiona sin registro)."""

    __tablename__ = "match_log"

    business_a: Mapped[int | None] = mapped_column(
        ForeignKey("businesses.id", ondelete="SET NULL"), index=True
    )
    business_b: Mapped[int | None] = mapped_column(
        ForeignKey("businesses.id", ondelete="SET NULL"), index=True
    )
    signals: Mapped[dict | None] = mapped_column(JSONB)
    score: Mapped[float | None] = mapped_column(Float)
    decision: Mapped[str | None] = mapped_column(String(20))  # ver constants.MATCH_DECISION
