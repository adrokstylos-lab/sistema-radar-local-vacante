"""Pruebas del orquestador (integración; usan la BD Docker)."""
import pytest
from sqlalchemy import select

from backend.app.db.models import TaskRun
from backend.app.db.session import SessionLocal
from backend.app.pipeline.orchestrator import TASKS, run_task

EXPECTED = {"discovery_scan", "business_refresh", "job_scan",
            "job_refresh", "closure_check", "data_quality"}


def test_registry():
    assert set(TASKS) == EXPECTED
    for fn, freq in TASKS.values():
        assert callable(fn) and isinstance(freq, str)


def test_unknown_task_raises():
    with pytest.raises(KeyError):
        run_task("no_existe")


def test_run_data_quality_records_history():
    stats = run_task("data_quality")
    assert "negocios" in stats
    session = SessionLocal()
    try:
        last = session.execute(
            select(TaskRun).where(TaskRun.name == "data_quality").order_by(TaskRun.id.desc())
        ).scalars().first()
        assert last is not None
        assert last.status == "done"
        assert last.stats == stats
    finally:
        session.close()


def test_job_scan_skips_without_key():
    # Sin JOOBLE_API_KEY debe saltar limpiamente (no fallar).
    from backend.app.core.config import settings
    if settings.jooble_api_key:
        pytest.skip("hay key configurada")
    stats = run_task("job_scan")
    assert "skipped" in stats
