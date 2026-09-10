"""Logger básico: consola + archivo en logs/app.log."""
from __future__ import annotations

import logging
from pathlib import Path

from backend.app.core.config import settings

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

_FMT = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(settings.log_level.upper())

        stream = logging.StreamHandler()
        stream.setFormatter(_FMT)
        logger.addHandler(stream)

        file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
        file_handler.setFormatter(_FMT)
        logger.addHandler(file_handler)

        logger.propagate = False
    return logger
