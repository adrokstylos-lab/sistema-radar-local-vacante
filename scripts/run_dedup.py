"""Ejecuta la deduplicación sobre los negocios reales y muestra el resultado.

Uso (con venv y BD Docker arriba):
    python scripts/run_dedup.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select  # noqa: E402

from backend.app.db.models import Business, MatchLog  # noqa: E402
from backend.app.db.session import SessionLocal  # noqa: E402
from backend.app.pipeline.dedup import dedup_zone  # noqa: E402


def main() -> None:
    session = SessionLocal()
    try:
        activos_antes = session.execute(
            select(func.count()).select_from(Business).where(
                Business.is_demo.is_(False), Business.merged_into_id.is_(None)
            )
        ).scalar()

        stats = dedup_zone(session)
        print("Resultado dedup:", stats)

        activos_despues = session.execute(
            select(func.count()).select_from(Business).where(
                Business.is_demo.is_(False), Business.merged_into_id.is_(None)
            )
        ).scalar()
        print(f"Negocios canónicos: {activos_antes} -> {activos_despues}")

        # Registro de decisiones (trazabilidad)
        rows = session.execute(
            select(MatchLog.decision, func.count()).group_by(MatchLog.decision)
        ).all()
        print("match_log:", {d: n for d, n in rows})
    finally:
        session.close()


if __name__ == "__main__":
    main()
