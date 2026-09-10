"""Pruebas del pipeline de vacantes (sin BD)."""
from backend.app.pipeline.jobs import classify_title, infer_scope, parse_salary
from backend.app.providers.jobs.jooble import parse_jooble


def test_classify_title():
    assert classify_title("Mesero/a") == "mesero"
    assert classify_title("Ayudante de cocina") == "ayudante_cocina"
    assert classify_title("Cajero/a de mostrador") == "cajero"
    assert classify_title("Bartender") == "bartender"
    assert classify_title("Gerente de sucursal") == "gerente"
    assert classify_title("Desarrollador de software") is None


def test_parse_salary_range_month():
    s = parse_salary("$7,000 - $9,000 al mes")
    assert s["salary_min"] == 7000 and s["salary_max"] == 9000
    assert s["currency"] == "MXN" and s["salary_period"] == "mes"


def test_parse_salary_single_day():
    s = parse_salary("$180 por día")
    assert s["salary_min"] == 180 and s["salary_max"] == 180
    assert s["salary_period"] == "dia"


def test_parse_salary_empty():
    s = parse_salary(None)
    assert s == {"salary_min": None, "salary_max": None, "currency": None, "salary_period": None}


class _Chain:
    pass


def test_infer_scope():
    # ubicación en el municipio -> sucursal
    assert infer_scope("Cuautitlán Izcalli, Méx.", "Cuautitlán Izcalli", None) == "sucursal"
    # cadena conocida pero otra ciudad -> corporativa
    assert infer_scope("Ciudad de México", "Cuautitlán Izcalli", _Chain()) == "corporativa"
    # sin ubicación ni cadena -> ciudad_desconocida
    assert infer_scope(None, "Cuautitlán Izcalli", None) == "ciudad_desconocida"


def test_parse_jooble():
    payload = {
        "jobs": [
            {"title": "Mesero", "company": "Toks", "location": "Cuautitlán",
             "salary": "$8000", "snippet": "desc", "link": "https://x/1", "id": 1, "updated": "2026-09-01"},
            {"title": "", "link": "https://x/2"},          # sin título -> descartado
            {"title": "Cocinero", "link": None},            # sin link -> descartado
        ]
    }
    out = parse_jooble(payload)
    assert len(out) == 1
    assert out[0]["title"] == "Mesero"
    assert out[0]["source_url"] == "https://x/1"
    assert out[0]["external_id"] == "1"
