"""Ejecuta el descubrimiento geográfico en la zona prioritaria (Cofradía de San
Miguel por defecto), usando OpenStreetMap/Overpass.

Pasos:
  1. Geocodifica el centro de la zona con Nominatim (confirma la coordenada).
  2. Hace upsert de la zona en la BD con el centro confirmado.
  3. Descubre negocios en el radio y los guarda.

Uso (con venv y BD Docker arriba):
    python scripts/run_discovery.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select  # noqa: E402

from backend.app.core.zones import get_primary_zone_config, upsert_zone  # noqa: E402
from backend.app.db.models import Business, BusinessLocation  # noqa: E402
from backend.app.db.session import SessionLocal  # noqa: E402
from backend.app.pipeline.discovery import discover_zone  # noqa: E402
from backend.app.providers.openstreetmap.nominatim import NominatimGeocoder  # noqa: E402
from backend.app.providers.openstreetmap.overpass import OverpassPlaceProvider  # noqa: E402


def _haversine_m(lat1, lng1, lat2, lng2) -> float:
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def main() -> None:
    cfg = get_primary_zone_config()
    print(f"Zona: {cfg['name']} ({cfg.get('municipality')}, {cfg.get('state')})")

    lat, lng = cfg.get("center_lat"), cfg.get("center_lng")

    # 1) Confirmar centro con geocoder
    query = ", ".join(
        p for p in (cfg["name"], cfg.get("municipality"), cfg.get("state"), cfg.get("country")) if p
    )
    try:
        geo = NominatimGeocoder().geocode(query)
    except Exception as exc:  # noqa: BLE001
        geo = None
        print(f"  [aviso] geocoder no disponible ({exc}); uso coordenada de config.")
    if geo:
        dist = _haversine_m(lat, lng, geo["lat"], geo["lng"]) if lat and lng else None
        print(f"  Geocoder: {geo['lat']:.5f}, {geo['lng']:.5f}  ({geo.get('display_name')})")
        if dist is not None:
            print(f"  Config aprox:  {lat}, {lng}  (a {dist:.0f} m del punto geocodificado)")
        lat, lng = geo["lat"], geo["lng"]

    radius_m = cfg.get("radius_m", 1800)
    print(f"  Centro usado: {lat:.5f}, {lng:.5f}  |  radio: {radius_m} m")

    session = SessionLocal()
    try:
        zone = upsert_zone(session, cfg, center_lat=lat, center_lng=lng)
        session.commit()

        provider = OverpassPlaceProvider()
        stats = discover_zone(session, zone, provider, lat, lng, radius_m)
        print("Resultado:", stats)

        # Muestra: categorías encontradas y 5 negocios más cercanos al centro
        by_cat = session.execute(
            select(Business.primary_category, func.count())
            .where(Business.is_demo.is_(False))
            .group_by(Business.primary_category)
            .order_by(func.count().desc())
        ).all()
        print("Por categoría:", {c or "sin_categoria": n for c, n in by_cat})
    finally:
        session.close()


if __name__ == "__main__":
    main()
