"""Pipeline de vacantes: clasificación de puesto, parseo de salario, inferencia
de alcance (sucursal/corporativa/ciudad_desconocida), deduplicación e ingesta.

Principio: no afirmar más de lo que el dato permite. Si no se puede atribuir a
una sucursal concreta, se marca el alcance con la incertidumbre correspondiente.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.logging import get_logger
from backend.app.db.models import Chain, Job, JobSource, SourceRequest
from backend.app.pipeline.normalize import normalize_name, strip_accents
from backend.app.providers.base import JobProvider

logger = get_logger("radar.jobs")

# Puestos prioritarios -> palabras clave (orden: más específico primero).
# Sin acentos y en minúsculas (se comparan tras strip_accents).
TITLE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("ayudante_cocina", ["ayudante de cocina", "auxiliar de cocina", "pinche"]),
    ("ayudante_general", ["ayudante general", "auxiliar general", "ayudante"]),
    ("lavaloza", ["lavaloza", "lavalozas", "lavaplatos", "steward"]),
    ("garrotero", ["garrotero", "garrotera", "busser"]),
    ("bartender", ["bartender", "cantinero", "barman", "barwoman"]),
    ("barista", ["barista"]),
    ("mesero", ["mesero", "mesera", "waiter", "waitress"]),
    ("cocinero", ["cocinero", "cocinera", "chef", "parrillero"]),
    ("hostess", ["hostess", "anfitrion", "anfitriona", "host"]),
    ("cajero", ["cajero", "cajera", "cashier"]),
    ("repartidor", ["repartidor", "repartidora", "reparto", "delivery", "mensajero", "motorepartidor"]),
    ("gerente", ["gerente", "subgerente", "manager"]),
    ("supervisor", ["supervisor", "supervisora"]),
    ("encargado", ["encargado", "encargada"]),
    ("limpieza", ["limpieza", "intendencia", "aseo", "sanitizacion"]),
    ("atencion_cliente", ["atencion a cliente", "atencion al cliente", "servicio al cliente", "customer service"]),
]


def classify_title(title: str) -> str | None:
    """Devuelve la categoría de puesto o None (no fuerza una clasificación)."""
    text = strip_accents(title or "").lower()
    for category, keywords in TITLE_KEYWORDS:
        if any(kw in text for kw in keywords):
            return category
    return None


_NUM = r"\$?\s*([\d]{1,3}(?:[,\.\s]\d{3})*(?:\.\d+)?)"
_PERIODS = {
    "hora": "hora", "hr": "hora",
    "dia": "dia",
    "semana": "semana",
    "quincena": "quincena", "quincenal": "quincena",
    "mes": "mes", "mensual": "mes",
    "ano": "ano", "anual": "ano",
}


def parse_salary(text: str | None) -> dict[str, Any]:
    """Extrae min/max/moneda/periodo de un texto libre. Lo no reconocido -> None."""
    result: dict[str, Any] = {"salary_min": None, "salary_max": None,
                              "currency": None, "salary_period": None}
    if not text:
        return result
    t = strip_accents(text).lower()
    nums = [float(n.replace(",", "").replace(" ", "")) for n in re.findall(_NUM, t)]
    if nums:
        result["salary_min"] = nums[0]
        result["salary_max"] = nums[1] if len(nums) > 1 else nums[0]
        result["currency"] = "MXN"  # contexto MX; el símbolo $ se asume peso
    for token, period in _PERIODS.items():
        if re.search(rf"\b{token}\b", t):
            result["salary_period"] = period
            break
    return result


def _match_chain(session: Session, company: str | None) -> Chain | None:
    if not company:
        return None
    nn = normalize_name(company)
    # coincidencia exacta o por contención (p. ej. "Burger King México" ~ "burger king")
    chains = session.execute(select(Chain).where(Chain.is_demo.is_(False))).scalars().all()
    for c in chains:
        if c.normalized_name == nn or c.normalized_name in nn or nn in c.normalized_name:
            return c
    return None


def infer_scope(location: str | None, municipality: str, chain: Chain | None) -> str:
    """Alcance geográfico honesto según lo que sabemos."""
    if location:
        loc = strip_accents(location).lower()
        muni = strip_accents(municipality).lower()
        # comparar por el primer término del municipio (p. ej. "cuautitlan")
        if muni.split()[0] in loc:
            return "sucursal"  # está en nuestra ciudad; sucursal exacta sin resolver
    if chain is not None:
        return "corporativa"  # cadena conocida pero ubicación no confirmada en la zona
    return "ciudad_desconocida"


def _in_region(location: str | None, allowed_terms: list[str] | None) -> bool:
    """True si la ubicación pertenece a la región permitida. Si no hay filtro,
    todo pasa. Si hay filtro y la ubicación es desconocida, se descarta (evita
    ingerir vacantes de otros países, p. ej. resultados de EE.UU. de Jooble)."""
    if not allowed_terms:
        return True
    if not location:
        return False
    loc = strip_accents(location).lower()
    return any(t in loc for t in allowed_terms)


def ingest_jobs(
    session: Session,
    provider: JobProvider,
    queries: list[dict[str, str]],
    municipality: str,
    demo: bool = False,
    allowed_location_terms: list[str] | None = None,
) -> dict[str, int]:
    now = datetime.now(timezone.utc)
    stats = {"encontrados": 0, "creados": 0, "omitidos_duplicados": 0,
             "omitidos_fuera_region": 0, "clasificados": 0}

    for q in queries:
        records = provider.search_jobs(keywords=q["keywords"], location=q["location"])
        stats["encontrados"] += len(records)
        _log_request(session, provider, results=len(records))

        # URLs ya presentes (dedup) para este alcance de datos (demo vs real)
        existing = set(
            session.execute(
                select(Job.source_url).where(Job.is_demo.is_(demo), Job.source_url.isnot(None))
            ).scalars()
        )

        for rec in records:
            url = rec.get("source_url")
            if url and url in existing:
                stats["omitidos_duplicados"] += 1
                continue

            if not _in_region(rec.get("location"), allowed_location_terms):
                stats["omitidos_fuera_region"] += 1
                continue

            category = classify_title(rec["title"])
            if category:
                stats["clasificados"] += 1
            chain = _match_chain(session, rec.get("company"))
            scope = infer_scope(rec.get("location"), municipality, chain)
            sal = parse_salary(rec.get("salary"))

            job = Job(
                chain_id=chain.id if chain else None,
                title=rec["title"],
                title_category=category,
                description=rec.get("description"),
                address=rec.get("location"),
                salary_min=sal["salary_min"],
                salary_max=sal["salary_max"],
                currency=sal["currency"],
                salary_period=sal["salary_period"],
                detected_at=now,
                last_verified_at=now,
                source=provider.name,
                source_url=url,
                status="activa",       # aparece listada en el agregador
                scope=scope,
                confidence="probable",  # los agregadores pueden ir con retraso
                is_demo=demo,
            )
            job.sources.append(
                JobSource(provider=provider.name, raw=rec, fetched_at=now)
            )
            session.add(job)
            if url:
                existing.add(url)
            stats["creados"] += 1

    session.commit()
    logger.info("Ingesta de vacantes: %s", stats)
    return stats


def _log_request(session: Session, provider: JobProvider, *, results: int) -> None:
    meta = getattr(provider, "last_result", None)
    session.add(
        SourceRequest(
            provider=provider.name,
            endpoint=getattr(meta, "url", None),
            response_cached=False,
            status_code=getattr(meta, "status_code", None),
            latency_ms=getattr(meta, "latency_ms", None),
            results_count=results,
        )
    )
