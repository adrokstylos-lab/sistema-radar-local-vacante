"""Partición geográfica en celdas (grid) con clave geohash, para escanear áreas
grandes de forma eficiente y sin consultas redundantes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def geohash_encode(lat: float, lng: float, precision: int = 6) -> str:
    """Geohash estándar (base32). Sirve como clave de celda/cobertura."""
    lat_lo, lat_hi = -90.0, 90.0
    lng_lo, lng_hi = -180.0, 180.0
    bits = [16, 8, 4, 2, 1]
    out: list[str] = []
    bit = 0
    ch = 0
    even = True
    while len(out) < precision:
        if even:
            mid = (lng_lo + lng_hi) / 2
            if lng > mid:
                ch |= bits[bit]
                lng_lo = mid
            else:
                lng_hi = mid
        else:
            mid = (lat_lo + lat_hi) / 2
            if lat > mid:
                ch |= bits[bit]
                lat_lo = mid
            else:
                lat_hi = mid
        even = not even
        if bit < 4:
            bit += 1
        else:
            out.append(_BASE32[ch])
            bit = 0
            ch = 0
    return "".join(out)


@dataclass
class Cell:
    geohash: str
    center_lat: float
    center_lng: float
    radius_m: int          # radio de círculo que cubre la celda (con solape)
    bbox: tuple[float, float, float, float]  # (min_lat, min_lng, max_lat, max_lng)


def _cell_radius_m(cell_km: float) -> int:
    # media diagonal de un cuadrado de lado cell_km, en metros (cobertura total)
    return int(cell_km * 1000 * math.sqrt(2) / 2)


def bbox_grid(min_lat, min_lng, max_lat, max_lng, cell_km: float = 1.5,
              geohash_precision: int = 6) -> list[Cell]:
    """Divide un bounding box en celdas ~cell_km de lado."""
    lat_step = cell_km / 111.0
    cells: list[Cell] = []
    radius = _cell_radius_m(cell_km)
    lat = min_lat
    while lat < max_lat:
        clat = min(lat + lat_step / 2, max_lat)
        lng_step = cell_km / (111.0 * max(math.cos(math.radians(clat)), 0.01))
        lng = min_lng
        while lng < max_lng:
            clng = min(lng + lng_step / 2, max_lng)
            cells.append(Cell(
                geohash=geohash_encode(clat, clng, geohash_precision),
                center_lat=round(clat, 6), center_lng=round(clng, 6),
                radius_m=radius,
                bbox=(round(lat, 6), round(lng, 6),
                      round(min(lat + lat_step, max_lat), 6),
                      round(min(lng + lng_step, max_lng), 6)),
            ))
            lng += lng_step
        lat += lat_step
    return cells


def circle_grid(center_lat, center_lng, radius_m: int, cell_km: float = 1.5,
                geohash_precision: int = 6) -> list[Cell]:
    """Genera celdas que cubren un círculo (centro + radio)."""
    d_lat = radius_m / 111000.0
    d_lng = radius_m / (111000.0 * max(math.cos(math.radians(center_lat)), 0.01))
    cells = bbox_grid(center_lat - d_lat, center_lng - d_lng,
                      center_lat + d_lat, center_lng + d_lng, cell_km, geohash_precision)
    # conservar celdas cuyo centro cae dentro del radio (+ media celda de margen)
    margin = _cell_radius_m(cell_km)
    keep = []
    for c in cells:
        dist = _haversine_m(center_lat, center_lng, c.center_lat, c.center_lng)
        if dist <= radius_m + margin:
            keep.append(c)
    return keep


def _haversine_m(lat1, lng1, lat2, lng2) -> float:
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
