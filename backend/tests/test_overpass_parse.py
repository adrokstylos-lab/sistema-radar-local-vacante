"""Prueba de parseo de una respuesta Overpass (sin red)."""
from backend.app.providers.openstreetmap.overpass import classify, parse_elements

SAMPLE = {
    "elements": [
        {  # node con nombre y categoría -> se incluye
            "type": "node",
            "id": 1,
            "lat": 19.6835,
            "lon": -99.2145,
            "tags": {"amenity": "restaurant", "name": "El Buen Sabor", "phone": "+52 55 1234"},
        },
        {  # way con center -> se incluye usando center
            "type": "way",
            "id": 2,
            "center": {"lat": 19.6820, "lon": -99.2160},
            "tags": {"shop": "bakery", "name": "Panadería La Espiga"},
        },
        {  # sin nombre -> se descarta
            "type": "node",
            "id": 3,
            "lat": 19.68,
            "lon": -99.21,
            "tags": {"amenity": "cafe"},
        },
        {  # categoría no relevante -> se descarta
            "type": "node",
            "id": 4,
            "lat": 19.68,
            "lon": -99.21,
            "tags": {"amenity": "pharmacy", "name": "Farmacia X"},
        },
    ]
}


def test_classify():
    assert classify({"amenity": "restaurant"}) == "restaurante"
    assert classify({"shop": "bakery"}) == "panaderia"
    assert classify({"tourism": "hotel"}) == "hotel"
    assert classify({"amenity": "pharmacy"}) is None


def test_parse_filters_and_maps():
    out = parse_elements(SAMPLE)
    assert len(out) == 2
    names = {r["name"] for r in out}
    assert names == {"El Buen Sabor", "Panadería La Espiga"}
    first = next(r for r in out if r["name"] == "El Buen Sabor")
    assert first["provider_place_id"] == "osm:node/1"
    assert first["category"] == "restaurante"
    assert first["lat"] == 19.6835 and first["lng"] == -99.2145
