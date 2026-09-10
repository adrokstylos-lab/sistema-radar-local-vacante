"""Ejecuta una tarea programada (para cron / Programador de tareas / GitHub Actions).

Uso:
    python scripts/run_task.py --list
    python scripts/run_task.py <nombre>

Sale con código != 0 si la tarea falla (para que el agendador detecte el error).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app.pipeline.orchestrator import TASKS, run_task  # noqa: E402


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "--list"):
        print("Tareas disponibles (frecuencia sugerida):")
        for name, (_fn, freq) in TASKS.items():
            print(f"  {name:18} {freq}")
        return 0

    name = argv[0]
    try:
        stats = run_task(name)
        print(f"[OK] {name}: {stats}")
        return 0
    except KeyError as exc:
        print(f"[ERROR] {exc}")
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"[FALLO] {name}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
