"""Demostración del escalado por grid: escanea un bbox PEQUEÑO por celdas
(gentil con Overpass), registra la cobertura por celda y omite celdas ya
escaneadas al re-ejecutar.

Uso:
    python scripts/run_grid_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.core.zones import get_primary_zone_config, upsert_zone  # noqa: E402
from backend.app.db.session import SessionLocal  # noqa: E402
from backend.app.pipeline.discovery import discover_grid  # noqa: E402
from backend.app.pipeline.grid import bbox_grid  # noqa: E402
from backend.app.providers.openstreetmap.overpass import OverpassPlaceProvider  # noqa: E402


def main() -> None:
    # bbox pequeño alrededor de Cofradía (solo unas pocas celdas, para no
    # sobrecargar Overpass). Escalar cambiando el bbox / cell_km.
    cells = bbox_grid(19.675, -99.235, 19.700, -99.210, cell_km=1.5)
    print(f"Celdas generadas: {len(cells)}  (geohashes: {[c.geohash for c in cells]})")

    session = SessionLocal()
    try:
        cfg = get_primary_zone_config()
        zone = upsert_zone(session, cfg)
        session.commit()

        provider = OverpassPlaceProvider()
        stats = discover_grid(session, zone, provider, cells, skip_recent_days=7)
        print("Resultado grid:", stats)
    finally:
        session.close()


if __name__ == "__main__":
    main()
