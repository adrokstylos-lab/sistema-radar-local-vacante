"""Ejecuta la búsqueda REAL de vacantes en Jooble para las franquicias detectadas.

Requiere JOOBLE_API_KEY en .env (límite: 500 peticiones de por vida -> se
consulta solo una vez por cadena). Si no hay key, explica cómo obtenerla y sale.

Uso:
    python scripts/run_jobs.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from backend.app.core.config import settings  # noqa: E402
from backend.app.core.zones import get_primary_zone_config  # noqa: E402
from backend.app.db.models import Chain  # noqa: E402
from backend.app.db.session import SessionLocal  # noqa: E402
from backend.app.pipeline.jobs import ingest_jobs  # noqa: E402


def main() -> None:
    if not settings.jooble_api_key:
        print(
            "No hay JOOBLE_API_KEY en .env.\n"
            "Solicítala gratis en https://jooble.org/api/about y añádela a .env.\n"
            "Mientras tanto, prueba el pipeline con: python scripts/run_jobs_demo.py"
        )
        return

    from backend.app.providers.jobs.jooble import JoobleJobProvider

    cfg = get_primary_zone_config()
    municipality = cfg.get("municipality", "")
    location = f"{municipality}, {cfg.get('state', '')}".strip(", ")

    session = SessionLocal()
    try:
        chains = session.execute(
            select(Chain.name).where(Chain.is_demo.is_(False)).order_by(Chain.name)
        ).scalars().all()
        if not chains:
            print("No hay franquicias detectadas todavía. Corre run_discovery.py + run_enrich.py.")
            return

        # Una consulta por franquicia (respeta el límite de 500 de por vida).
        queries = [{"keywords": name, "location": location} for name in chains]
        provider = JoobleJobProvider()
        # Salvaguarda: solo aceptar vacantes de la región (evita ruido de otros países).
        mx_terms = ["cuautitlan", "izcalli", "estado de mexico", "edomex", "cdmx",
                    "ciudad de mexico", "naucalpan", "tlalnepantla", "atizapan"]
        stats = ingest_jobs(session, provider, queries, municipality=municipality,
                            demo=False, allowed_location_terms=mx_terms)
        print("Ingesta REAL (Jooble):", stats)
    finally:
        session.close()


if __name__ == "__main__":
    main()
