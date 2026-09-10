"""Configuración de pruebas: siembra datos DEMO (idempotente) para que las
pruebas de integración sean reproducibles sin depender de red ni de datos reales.
"""
import pytest

from backend.app.db.seed import run as seed_demo


@pytest.fixture(scope="session", autouse=True)
def _seed_demo_data():
    seed_demo()
    yield
