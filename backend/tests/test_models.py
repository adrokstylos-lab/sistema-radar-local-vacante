"""Pruebas de los modelos ORM (no requieren base de datos)."""
from geoalchemy2 import Geography

from backend.app.db.base import Base
from backend.app.db import models  # noqa: F401  (registra las tablas)

EXPECTED_TABLES = {
    "geographic_zones",
    "chains",
    "businesses",
    "business_locations",
    "business_hours",
    "business_contacts",
    "business_sources",
    "business_snapshots",
    "jobs",
    "job_sources",
    "job_snapshots",
    "scans",
    "source_requests",
    "match_log",
    "task_runs",
}


def test_all_tables_registered():
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_geography_columns_are_srid_4326():
    loc = Base.metadata.tables["business_locations"]
    geog = loc.columns["geog"]
    assert isinstance(geog.type, Geography)
    assert geog.type.srid == 4326


def test_demo_flag_present_on_core_tables():
    for table in ("businesses", "jobs", "chains", "geographic_zones"):
        assert "is_demo" in Base.metadata.tables[table].columns
