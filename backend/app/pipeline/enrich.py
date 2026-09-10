"""Enriquecimiento de negocios a partir de datos públicos ya recolectados
(etiquetas OpenStreetMap). No inventa datos: si un campo no existe, queda NULL.
Cada dato enriquecido conserva su fuente y confianza.
"""
from __future__ import annotations

import re
from datetime import datetime, time, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.logging import get_logger
from backend.app.db.models import Business, BusinessContact, BusinessHours, Chain
from backend.app.pipeline.normalize import normalize_name

logger = get_logger("radar.enrich")

# Etiquetas de servicio OSM -> clave interna
SERVICE_TAGS = {
    "delivery": "delivery",
    "takeaway": "takeout",
    "drive_through": "drive_through",
    "outdoor_seating": "outdoor_seating",
    "wheelchair": "wheelchair_accessible",
    "internet_access": "wifi",
    "air_conditioning": "air_conditioning",
    "reservation": "reservations",
}

# Contactos adicionales que pudieran no haberse capturado en el descubrimiento
ENRICH_CONTACT_TAGS = {
    "website": "web",
    "contact:website": "web",
    "email": "email",
    "contact:email": "email",
    "contact:facebook": "facebook",
    "contact:instagram": "instagram",
}

_DAYS = {"Mo": 0, "Tu": 1, "We": 2, "Th": 3, "Fr": 4, "Sa": 5, "Su": 6}


def _parse_days(token: str) -> set[int]:
    days: set[int] = set()
    for part in token.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            ia, ib = _DAYS[a], _DAYS[b]
            rng = range(ia, ib + 1) if ia <= ib else list(range(ia, 7)) + list(range(0, ib + 1))
            days.update(rng)
        else:
            days.add(_DAYS[part])
    return days


def _parse_time(t: str) -> time:
    h, m = t.split(":")
    hh = int(h)
    return time(23, 59) if hh >= 24 else time(hh, int(m))


def parse_opening_hours(value: str | None) -> list[tuple[int, time, time]]:
    """Parser pragmático de OSM opening_hours para los casos comunes.
    Devuelve [(día 0=Lu..6=Do, apertura, cierre)]. Ignora reglas que no entiende
    (no inventa)."""
    s = (value or "").strip()
    if not s:
        return []
    if s == "24/7":
        return [(d, time(0, 0), time(23, 59)) for d in range(7)]
    out: list[tuple[int, time, time]] = []
    for rule in s.split(";"):
        m = re.match(r"^([A-Za-z,\-]+)\s+(\d{1,2}:\d{2})-(\d{1,2}:\d{2})$", rule.strip())
        if not m:
            continue
        try:
            days = _parse_days(m.group(1))
            open_t, close_t = _parse_time(m.group(2)), _parse_time(m.group(3))
        except (KeyError, ValueError):
            continue
        out.extend((d, open_t, close_t) for d in sorted(days))
    return out


def get_or_create_chain(session: Session, brand: str) -> Chain:
    nn = normalize_name(brand)
    chain = session.execute(
        select(Chain).where(Chain.normalized_name == nn, Chain.is_demo.is_(False))
    ).scalar_one_or_none()
    if chain is None:
        chain = Chain(name=brand, normalized_name=nn, is_demo=False)
        session.add(chain)
        session.flush()
    return chain


def enrich_business(session: Session, business: Business, now: datetime) -> dict:
    src = next(
        (s for s in business.sources if s.provider == "openstreetmap" and s.raw), None
    )
    if src is None:
        return {}
    tags: dict = src.raw
    added: dict = {}

    # Tipo de comida
    if not business.food_type and tags.get("cuisine"):
        business.food_type = tags["cuisine"].replace(";", ", ").replace("_", " ")
        added["food_type"] = 1

    # Servicios
    services = dict(business.services or {})
    before = dict(services)
    for tag, key in SERVICE_TAGS.items():
        if tag in tags and key not in services:
            v = tags[tag]
            services[key] = True if v == "yes" else False if v == "no" else v
    if services != before:
        business.services = services
        added["services"] = len(services)

    # Cadena / franquicia
    if not business.chain_id and tags.get("brand"):
        chain = get_or_create_chain(session, tags["brand"])
        business.chain_id = chain.id
        added["chain"] = chain.name

    # Contactos que faltaran
    existing = {(c.type, c.value) for c in business.contacts}
    for tag, ctype in ENRICH_CONTACT_TAGS.items():
        val = tags.get(tag)
        if val and (ctype, val) not in existing:
            business.contacts.append(
                BusinessContact(type=ctype, value=val, source="openstreetmap", confidence="probable")
            )
            existing.add((ctype, val))
            added["contactos"] = added.get("contactos", 0) + 1

    # Horarios (solo si el negocio no tiene)
    if not business.hours:
        parsed = parse_opening_hours(tags.get("opening_hours"))
        for d, o, c in parsed:
            business.hours.append(
                BusinessHours(day_of_week=d, open_time=o, close_time=c,
                              source="openstreetmap", confidence="probable")
            )
        if parsed:
            added["horarios"] = len(parsed)

    if added:
        business.last_verified_at = now
    return added


def enrich_all(session: Session) -> dict:
    now = datetime.now(timezone.utc)
    businesses = session.execute(
        select(Business).where(
            Business.is_demo.is_(False), Business.merged_into_id.is_(None)
        )
    ).scalars().all()

    totals = {"negocios": 0, "con_cambios": 0, "food_type": 0, "services": 0,
              "chain": 0, "contactos": 0, "horarios": 0}
    for b in businesses:
        totals["negocios"] += 1
        added = enrich_business(session, b, now)
        if added:
            totals["con_cambios"] += 1
        for k in ("food_type", "chain"):
            if k in added:
                totals[k] += 1
        for k in ("services", "contactos", "horarios"):
            totals[k] += added.get(k, 0)

    session.commit()
    logger.info("Enriquecimiento: %s", totals)
    return totals
