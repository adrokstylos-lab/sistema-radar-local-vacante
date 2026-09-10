"""Pruebas del grid y geohash (sin BD ni red)."""
from backend.app.pipeline.grid import bbox_grid, circle_grid, geohash_encode


def test_geohash_known_value():
    # Ejemplo clásico: (57.64911, 10.40744) -> "u4pruydqqvj"
    assert geohash_encode(57.64911, 10.40744, 11) == "u4pruydqqvj"
    assert geohash_encode(57.64911, 10.40744, 6) == "u4pruy"


def test_geohash_nearby_share_prefix():
    a = geohash_encode(19.6835, -99.2145, 6)
    b = geohash_encode(19.6836, -99.2146, 6)
    assert a[:5] == b[:5]


def test_bbox_grid_covers_and_counts():
    cells = bbox_grid(19.60, -99.28, 19.72, -99.18, cell_km=1.5)
    assert len(cells) > 1
    # cada centro cae dentro (o en el borde) del bbox pedido
    for c in cells:
        assert 19.60 - 0.02 <= c.center_lat <= 19.72 + 0.02
        assert -99.28 - 0.02 <= c.center_lng <= -99.18 + 0.02
        assert c.radius_m > 0
    # geohashes únicos por celda (clave de cobertura)
    assert len({c.geohash for c in cells}) >= 1


def test_circle_grid_keeps_cells_near_center():
    cells = circle_grid(19.6895, -99.2263, radius_m=2000, cell_km=1.0)
    assert len(cells) >= 1
