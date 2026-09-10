"""Normalización de valores para comparación/deduplicación."""
from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlparse


def strip_accents(text: str) -> str:
    """Quita acentos/diacríticos (á->a, ñ->n) para comparaciones robustas."""
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_name(name: str) -> str:
    """Minúsculas y espacios colapsados."""
    return " ".join((name or "").lower().split())


def normalize_phone(value: str | None) -> str | None:
    """Solo dígitos; se conservan los últimos 10 (número nacional MX) para comparar."""
    digits = re.sub(r"\D", "", value or "")
    if not digits:
        return None
    return digits[-10:] if len(digits) >= 10 else digits


def extract_domain(url: str | None) -> str | None:
    """Dominio en minúsculas sin 'www.'."""
    if not url:
        return None
    u = url.strip()
    if "://" not in u:
        u = "http://" + u
    net = urlparse(u).netloc.lower()
    if net.startswith("www."):
        net = net[4:]
    return net or None


def normalize_social(value: str | None) -> str | None:
    """Handle de red social sin '@' ni URL."""
    if not value:
        return None
    v = value.strip().lower()
    if "://" in v or "/" in v:
        v = v.rstrip("/").split("/")[-1]
    return v.lstrip("@") or None
