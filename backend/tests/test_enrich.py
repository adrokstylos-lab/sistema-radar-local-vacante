"""Pruebas del parser de horarios y mapeos de enriquecimiento (sin BD)."""
from datetime import time

from backend.app.pipeline.enrich import SERVICE_TAGS, parse_opening_hours


def test_parse_opening_hours_burger_king():
    s = "Mo-Th 10:00-21:00; Fr-Sa 10:00-22:00; Su 10:00-21:00"
    out = parse_opening_hours(s)
    # 4 (Mo-Th) + 2 (Fr-Sa) + 1 (Su) = 7 filas
    assert len(out) == 7
    by_day = {d: (o, c) for d, o, c in out}
    assert by_day[0] == (time(10, 0), time(21, 0))   # lunes
    assert by_day[5] == (time(10, 0), time(22, 0))   # sábado
    assert by_day[6] == (time(10, 0), time(21, 0))   # domingo


def test_parse_opening_hours_24_7():
    out = parse_opening_hours("24/7")
    assert len(out) == 7
    assert all(o == time(0, 0) for _, o, _ in out)


def test_parse_opening_hours_wraparound_and_list():
    # Fr-Mo abarca Vi, Sa, Do, Lu ; lista We,Su
    assert len(parse_opening_hours("Fr-Mo 08:00-12:00")) == 4
    assert len(parse_opening_hours("We,Su 09:00-14:00")) == 2


def test_parse_opening_hours_unparseable_returns_empty():
    assert parse_opening_hours("") == []
    assert parse_opening_hours("por las tardes") == []


def test_service_tags_mapping_present():
    assert SERVICE_TAGS["delivery"] == "delivery"
    assert SERVICE_TAGS["takeaway"] == "takeout"
