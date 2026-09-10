"""Geocoder basado en Nominatim (OpenStreetMap, gratis).

Política de uso: máximo ~1 req/seg y User-Agent identificativo (ya configurado
en el cliente HTTP). Uso de bajo volumen: confirmar el centro de una zona.
"""
from __future__ import annotations

from typing import Any

from backend.app.core.config import settings
from backend.app.core.http import fetch_json
from backend.app.providers.base import GeocoderProvider


class NominatimGeocoder(GeocoderProvider):
    name = "nominatim"

    def geocode(self, address: str) -> dict[str, Any] | None:
        result = fetch_json(
            "GET",
            settings.nominatim_url,
            params={"q": address, "format": "jsonv2", "limit": 1},
        )
        items = result.data
        if not items:
            return None
        top = items[0]
        return {
            "lat": float(top["lat"]),
            "lng": float(top["lon"]),
            "display_name": top.get("display_name"),
            "raw": top,
        }

    def reverse_geocode(self, lat: float, lng: float) -> dict[str, Any] | None:
        # No necesario en Fase 4; se implementará si hace falta.
        raise NotImplementedError
