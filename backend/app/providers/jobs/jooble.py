"""Adaptador de vacantes Jooble (agregador con API gratuita).

IMPORTANTE: la API de Jooble tiene un límite de 500 peticiones DE POR VIDA por
key. El pipeline debe cachear y consultar con moderación (solo franquicias/zona).

Incluye también un FixtureJobProvider para demostrar el pipeline sin red ni key.
"""
from __future__ import annotations

from typing import Any

from backend.app.core.config import settings
from backend.app.core.http import HttpResult, fetch_json
from backend.app.providers.base import JobProvider


def parse_jooble(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Convierte la respuesta de Jooble en registros uniformes (sin red)."""
    out: list[dict[str, Any]] = []
    for j in payload.get("jobs", []):
        title = (j.get("title") or "").strip()
        link = j.get("link")
        if not title or not link:
            continue
        out.append(
            {
                "title": title,
                "company": (j.get("company") or "").strip() or None,
                "location": (j.get("location") or "").strip() or None,
                "salary": (j.get("salary") or "").strip() or None,
                "description": (j.get("snippet") or "").strip() or None,
                "source_url": link,
                "posted_at_raw": j.get("updated"),
                "external_id": str(j.get("id")) if j.get("id") is not None else None,
            }
        )
    return out


class JoobleJobProvider(JobProvider):
    name = "jooble"

    def __init__(self) -> None:
        self.last_result: HttpResult | None = None
        if not settings.jooble_api_key:
            raise RuntimeError(
                "Falta JOOBLE_API_KEY en .env. Solicítala gratis en "
                "https://jooble.org/api/about (límite: 500 peticiones de por vida)."
            )

    def search_jobs(self, *, keywords: str, location: str, **kwargs: Any) -> list[dict[str, Any]]:
        url = f"https://jooble.org/api/{settings.jooble_api_key}"
        result = fetch_json("POST", url, json={"keywords": keywords, "location": location})
        self.last_result = result
        return parse_jooble(result.data)

    def get_job_details(self, job_id: str) -> dict:
        raise NotImplementedError("Jooble entrega todos los datos en search_jobs().")


# Muestra realista con forma de salida ya parseada, para demostrar el pipeline
# sin red ni key. Marca los resultados como DEMO en la ingesta.
_FIXTURE_JOBS: list[dict[str, Any]] = [
    {"title": "Mesero/a", "company": "Toks", "location": "Cuautitlán Izcalli, Méx.",
     "salary": "$7,000 - $9,000 al mes", "description": "Atención a clientes en piso.",
     "source_url": "https://demo.jooble.org/1", "posted_at_raw": "2026-09-01", "external_id": "1"},
    {"title": "Ayudante de cocina", "company": "Burger King", "location": "Cuautitlán Izcalli",
     "salary": "$180 por día", "description": "Apoyo en cocina.",
     "source_url": "https://demo.jooble.org/2", "posted_at_raw": "2026-09-03", "external_id": "2"},
    {"title": "Cajero/a", "company": "Tienda Local", "location": "Cuautitlán Izcalli",
     "salary": None, "description": "Manejo de caja.",
     "source_url": "https://demo.jooble.org/3", "posted_at_raw": "2026-09-05", "external_id": "3"},
    {"title": "Bartender", "company": "Bar Centro", "location": "Ciudad de México",
     "salary": "$12,000 mensual", "description": "Preparación de bebidas.",
     "source_url": "https://demo.jooble.org/4", "posted_at_raw": "2026-08-20", "external_id": "4"},
    {"title": "Mesero/a", "company": "Toks", "location": "Cuautitlán Izcalli, Méx.",
     "salary": "$7,000 - $9,000 al mes", "description": "Duplicado para probar dedup.",
     "source_url": "https://demo.jooble.org/1", "posted_at_raw": "2026-09-01", "external_id": "1"},
]


class FixtureJobProvider(JobProvider):
    """Devuelve una muestra fija (para demo/pruebas). No hace red."""

    name = "jooble"

    def __init__(self) -> None:
        self.last_result = None

    def search_jobs(self, *, keywords: str, location: str, **kwargs: Any) -> list[dict[str, Any]]:
        return list(_FIXTURE_JOBS)

    def get_job_details(self, job_id: str) -> dict:
        raise NotImplementedError
