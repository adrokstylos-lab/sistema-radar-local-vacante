"""Pruebas de la API (integración). Usan los datos DEMO sembrados por conftest,
por lo que son reproducibles sin red ni datos reales."""
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_stats():
    r = client.get("/stats", params={"include_demo": "true"})
    assert r.status_code == 200
    data = r.json()
    assert data["total_businesses"] >= 3
    assert isinstance(data["by_category"], dict)


def test_zones_has_cofradia():
    r = client.get("/zones", params={"include_demo": "true"})
    assert r.status_code == 200
    names = [z["name"] for z in r.json()]
    assert any("Cofradía" in n for n in names)


def test_businesses_list_and_coords():
    r = client.get("/businesses", params={"include_demo": "true", "limit": 100})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 3
    assert all(i["lat"] is not None and i["lng"] is not None for i in items)


def test_businesses_category_filter():
    r = client.get("/businesses", params={"include_demo": "true", "category": "restaurante", "limit": 100})
    assert r.status_code == 200
    cats = {i["primary_category"] for i in r.json()}
    assert cats == {"restaurante"} or not cats  # solo restaurantes (o vacío)


def test_business_detail_and_404():
    ids = [i["id"] for i in client.get("/businesses", params={"include_demo": "true", "limit": 1}).json()]
    assert ids, "debe haber al menos un negocio DEMO"
    r = client.get(f"/businesses/{ids[0]}")
    assert r.status_code == 200
    body = r.json()
    assert "contacts" in body and "hours" in body and "jobs" in body
    assert client.get("/businesses/99999999").status_code == 404


def test_jobs_demo_filter():
    r = client.get("/jobs", params={"include_demo": "true", "job_title": "mesero"})
    assert r.status_code == 200
    jobs = r.json()
    assert len(jobs) >= 1
    assert all(j["title_category"] == "mesero" for j in jobs)


def test_job_404():
    assert client.get("/jobs/99999999").status_code == 404


def test_health_db():
    r = client.get("/health/db")
    assert r.status_code == 200
    assert r.json()["database"] == "ok"
