"""Demuestra el pipeline de vacantes SIN red ni key (datos de ejemplo).
Los resultados se marcan como DEMO (is_demo=True).

Uso:
    python scripts/run_jobs_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select  # noqa: E402

from backend.app.db.models import Job  # noqa: E402
from backend.app.db.session import SessionLocal  # noqa: E402
from backend.app.pipeline.jobs import ingest_jobs  # noqa: E402
from backend.app.providers.jobs.jooble import FixtureJobProvider  # noqa: E402


def main() -> None:
    session = SessionLocal()
    try:
        provider = FixtureJobProvider()
        stats = ingest_jobs(
            session,
            provider,
            queries=[{"keywords": "mesero cocinero", "location": "Cuautitlán Izcalli"}],
            municipality="Cuautitlán Izcalli",
            demo=True,
        )
        print("Ingesta (DEMO):", stats)

        rows = session.execute(
            select(Job.title, Job.title_category, Job.scope, Job.salary_min, Job.salary_max, Job.chain_id)
            .where(Job.is_demo.is_(True), Job.source == "jooble")
            .order_by(Job.id)
        ).all()
        print("\nVacantes DEMO ingeridas:")
        for t, cat, scope, smin, smax, cid in rows:
            print(f"  - {t:22} cat={cat or '-':16} scope={scope:18} salario={smin}-{smax} cadena_id={cid}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
