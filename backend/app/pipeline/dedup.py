"""Deduplicación de negocios: señales, decisión con niveles de confianza y merge
controlado con trazabilidad en match_log.

Regla clave: nada 'dudoso' se fusiona automáticamente; queda registrado como
manual_review para revisión humana.
"""
from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz
from sqlalchemy import select, text, update
from sqlalchemy.orm import Session

from backend.app.core.logging import get_logger
from backend.app.db.models import (
    Business,
    BusinessContact,
    BusinessHours,
    BusinessLocation,
    BusinessSource,
    Job,
    MatchLog,
)
from backend.app.pipeline.normalize import (
    extract_domain,
    normalize_phone,
    normalize_social,
)

logger = get_logger("radar.dedup")

# Umbrales
DIST_EXACT = 75.0       # m
DIST_PROBABLE = 100.0   # m
DIST_DUDOSA = 150.0     # m
SIM_PROBABLE = 0.92
SIM_DUDOSA = 0.85

_SOCIAL_TYPES = {"facebook", "instagram", "tiktok", "linkedin", "whatsapp"}


@dataclass
class Signals:
    name_exact: bool
    name_sim: float
    distance_m: float
    phone_match: bool
    domain_match: bool
    social_match: bool

    def as_dict(self) -> dict:
        return {
            "name_exact": self.name_exact,
            "name_sim": round(self.name_sim, 3),
            "distance_m": round(self.distance_m, 1),
            "phone_match": self.phone_match,
            "domain_match": self.domain_match,
            "social_match": self.social_match,
        }


def decide(sig: Signals) -> tuple[str, str, float]:
    """Devuelve (decision, nivel, score). decision ∈ {auto_merge, manual_review, rejected}."""
    strong = (
        sig.phone_match
        or sig.domain_match
        or sig.social_match
        or (sig.name_exact and sig.distance_m <= DIST_EXACT)
    )
    if strong:
        return "auto_merge", "exacta_o_fuerte", 1.0
    if sig.name_sim >= SIM_PROBABLE and sig.distance_m <= DIST_PROBABLE:
        return "auto_merge", "probable", 0.9
    if sig.name_sim >= SIM_DUDOSA and sig.distance_m <= DIST_DUDOSA:
        return "manual_review", "dudosa", 0.7
    return "rejected", "ninguna", 0.0


def _contacts_index(session: Session, business_ids: list[int]) -> dict[int, dict[str, set]]:
    """Para cada negocio: conjuntos de teléfonos, dominios y redes normalizados."""
    idx: dict[int, dict[str, set]] = {
        bid: {"phones": set(), "domains": set(), "socials": set()} for bid in business_ids
    }
    rows = session.execute(
        select(BusinessContact.business_id, BusinessContact.type, BusinessContact.value).where(
            BusinessContact.business_id.in_(business_ids)
        )
    ).all()
    for bid, ctype, value in rows:
        if ctype in ("telefono", "whatsapp"):
            if p := normalize_phone(value):
                idx[bid]["phones"].add(p)
        if ctype == "web":
            if d := extract_domain(value):
                idx[bid]["domains"].add(d)
        if ctype in _SOCIAL_TYPES:
            if s := normalize_social(value):
                idx[bid]["socials"].add(s)
    return idx


def _min_distance_m(session: Session, a_id: int, b_id: int) -> float:
    val = session.execute(
        text(
            "SELECT MIN(ST_Distance(l1.geog, l2.geog)) "
            "FROM business_locations l1 JOIN business_locations l2 "
            "ON l1.business_id = :a AND l2.business_id = :b"
        ),
        {"a": a_id, "b": b_id},
    ).scalar()
    return float(val) if val is not None else float("inf")


def compute_signals(session: Session, a: Business, b: Business) -> Signals:
    idx = _contacts_index(session, [a.id, b.id])
    ca, cb = idx[a.id], idx[b.id]
    return Signals(
        name_exact=a.normalized_name == b.normalized_name,
        name_sim=fuzz.token_sort_ratio(a.normalized_name, b.normalized_name) / 100.0,
        distance_m=_min_distance_m(session, a.id, b.id),
        phone_match=bool(ca["phones"] & cb["phones"]),
        domain_match=bool(ca["domains"] & cb["domains"]),
        social_match=bool(ca["socials"] & cb["socials"]),
    )


_CHILD_FKS = [
    (BusinessLocation, "business_id"),
    (BusinessHours, "business_id"),
    (BusinessContact, "business_id"),
    (BusinessSource, "business_id"),
    (Job, "business_id"),
]


def merge(session: Session, canonical: Business, dup: Business) -> None:
    """Reasigna los hijos del duplicado al canónico y marca merged_into_id
    (reversible, sin borrar datos)."""
    for model, fk in _CHILD_FKS:
        session.execute(
            update(model).where(getattr(model, fk) == dup.id).values(**{fk: canonical.id})
        )
    dup.merged_into_id = canonical.id
    session.flush()


def _candidate_pairs(session: Session) -> list[tuple[int, int, float]]:
    """Pares de negocios reales, no fusionados, con ubicaciones a ≤ DIST_DUDOSA."""
    rows = session.execute(
        text(
            """
            SELECT l1.business_id AS a, l2.business_id AS b,
                   MIN(ST_Distance(l1.geog, l2.geog)) AS d
            FROM business_locations l1
            JOIN business_locations l2
              ON l1.business_id < l2.business_id
             AND ST_DWithin(l1.geog, l2.geog, :dist)
            JOIN businesses ba ON ba.id = l1.business_id
             AND NOT ba.is_demo AND ba.merged_into_id IS NULL
            JOIN businesses bb ON bb.id = l2.business_id
             AND NOT bb.is_demo AND bb.merged_into_id IS NULL
            GROUP BY l1.business_id, l2.business_id
            ORDER BY d ASC
            """
        ),
        {"dist": DIST_DUDOSA},
    ).all()
    return [(r.a, r.b, float(r.d)) for r in rows]


def dedup_zone(session: Session) -> dict[str, int]:
    stats = {"pares": 0, "auto_merge": 0, "manual_review": 0, "rejected": 0}
    canonical_of: dict[int, int] = {}

    def resolve(x: int) -> int:
        while x in canonical_of:
            x = canonical_of[x]
        return x

    for a_id, b_id, _d in _candidate_pairs(session):
        stats["pares"] += 1
        ca, cb = resolve(a_id), resolve(b_id)
        if ca == cb:
            continue
        a = session.get(Business, ca)
        b = session.get(Business, cb)
        if a is None or b is None:
            continue

        sig = compute_signals(session, a, b)
        decision, level, score = decide(sig)
        stats[decision] += 1

        if decision == "auto_merge":
            canonical, dup = (a, b) if a.id < b.id else (b, a)
            merge(session, canonical, dup)
            canonical_of[dup.id] = canonical.id
            session.add(
                MatchLog(business_a=canonical.id, business_b=dup.id,
                         signals={**sig.as_dict(), "nivel": level}, score=score, decision="auto_merge")
            )
        elif decision == "manual_review":
            session.add(
                MatchLog(business_a=a.id, business_b=b.id,
                         signals={**sig.as_dict(), "nivel": level}, score=score, decision="manual_review")
            )
        # 'rejected' no se registra (ruido)

    session.commit()
    logger.info("Dedup: %s", stats)
    return stats
