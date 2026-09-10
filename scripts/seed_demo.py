"""Carga datos DEMO (ver backend/app/db/seed.py). Idempotente; no toca datos reales.

Uso:
    python scripts/seed_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.db.seed import run  # noqa: E402

if __name__ == "__main__":
    print("Datos DEMO cargados:", run())
