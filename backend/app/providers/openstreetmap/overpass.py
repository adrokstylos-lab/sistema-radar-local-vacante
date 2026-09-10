"""Proveedor de lugares basado en OpenStreetMap vía Overpass API (gratis, sin key).

Busca establecimientos de comida/bebida/hospitalidad dentro de un radio y los
devuelve como registros crudos normalizados mínimamente. La clasificación de
categorías es un mapa tag->categoría, fácilmente modificable (no rígido).
"""
from __future__ import annotations

from typing import Any

from backend.app.core.config import settings
from backend.app.core.http import HttpResult, fetch_json
from backend.app.providers.base import PlaceProvider

# Mapas de tags OSM -> categoría interna. Modificables sin tocar la lógica.
AMENITY_MAP = {
    "restaurant": "restaurante",
    "cafe": "cafeteria",
    "bar": "bar",
    "pub": "bar",
    "fast_food": "comida_rapida",
    "food_court": "plaza_comida",
    "ice_cream": "heladeria",
    "nightclub": "antro",
    "biergarten": "bar",
}
SHOP_MAP = {
    "bakery": "panaderia",
    "pastry": "pasteleria",
    "confectionery": "dulceria",
    "coffee": "cafeteria",
}
TOURISM_MAP = {
    "hotel": "hotel",
    "guest_house": "hospedaje",
    "hostel": "hospedaje",
    "motel": "hotel",
}


def classify(tags: dict[str, str]) -> str | None:
    """Devuelve la categoría interna a partir de los tags OSM, o None."""
    if (a := tags.get("amenity")) in AMENITY_MAP:
        return AMENITY_MAP[a]
    if (s := tags.get("shop")) in SHOP_MAP:
        return SHOP_MAP[s]
    if (t := tags.get("tourism")) in TOURISM_MAP:
        return TOURISM_MAP[t]
    return None


def _build_query(lat: float, lng: float, radius_m: int) -> str:
    amenities = "|".join(AMENITY_MAP)
    shops = "|".join(SHOP_MAP)
    tourism = "|".join(TOURISM_MAP)
    around = f"around:{radius_m},{lat},{lng}"
    return f"""
[out:json][timeout:60];
(
  nwr["amenity"~"^({amenities})$"]({around});
  nwr["shop"~"^({shops})$"]({around});
  nwr["tourism"~"^({tourism})$"]({around});
);
out center tags;
""".strip()


def parse_elements(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Convierte la respuesta Overpass en registros crudos. Sin red (testeable)."""
    results: list[dict[str, Any]] = []
    for el in payload.get("elements", []):
        tags = el.get("tags") or {}
        name = tags.get("name")
        if not name:
            continue  # sin nombre no es un negocio identificable
        category = classify(tags)
        if category is None:
            continue
        # Coordenadas: nodes traen lat/lon; ways/relations traen "center".
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        results.append(
            {
                "provider_place_id": f"osm:{el.get('type')}/{el.get('id')}",
                "name": name,
                "category": category,
                "lat": float(lat),
                "lng": float(lon),
                "tags": tags,
            }
        )
    return results


class OverpassPlaceProvider(PlaceProvider):
    name = "openstreetmap"

    def __init__(self) -> None:
        self.last_result: HttpResult | None = None

    def search_places(
        self, *, lat: float, lng: float, radius_m: int, **kwargs: Any
    ) -> list[dict[str, Any]]:
        query = _build_query(lat, lng, radius_m)
        result = fetch_json("POST", settings.overpass_url, data={"data": query})
        self.last_result = result
        return parse_elements(result.data)

    def get_place_details(self, provider_place_id: str) -> dict:
        # OSM ya entrega todos los tags en search_places; no hay endpoint de
        # detalle independiente en Overpass.
        raise NotImplementedError(
            "Overpass devuelve los tags completos en search_places()."
        )
