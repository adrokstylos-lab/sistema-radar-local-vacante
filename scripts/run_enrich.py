"""Enriquece los negocios reales a partir de las etiquetas OSM ya guardadas.

Uso (con venv y BD Docker arriba):
    python scripts/run_enrich.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select  # noqa: E402

from backend.app.db.models import Business, BusinessHours, Chain  # noqa: E402
from backend.app.db.session import SessionLocal  # noqa: E402
from backend.app.pipeline.enrich import enrich_all  # noqa: E402


def main() -> None:
    session = SessionLocal()
    try:
        totals = enrich_all(session)
        print("Enriquecimiento:", totals)

        chains = session.execute(
            select(Chain.name).where(Chain.is_demo.is_(False)).order_by(Chain.name)
        ).scalars().all()
        print("Cadenas detectadas:", chains)

        n_hours = session.execute(
            select(func.count()).select_from(BusinessHours)
            .join(Business, Business.id == BusinessHours.business_id)
            .where(Business.is_demo.is_(False))
        ).scalar()
        print("Filas de horario (negocios reales):", n_hours)
    finally:
        session.close()


if __name__ == "__main__":
    main()
