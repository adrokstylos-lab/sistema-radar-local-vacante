"""Entorno de Alembic. Toma la URL de la BD desde la config del proyecto.

En Fase 3 se importarán los modelos para habilitar `--autogenerate`.
"""
from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy import engine_from_config, pool

from backend.app.core.config import settings
from backend.app.db.base import Base
from backend.app.db import models  # noqa: F401  (registra las tablas en Base.metadata)

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def include_object(obj, name, type_, reflected, compare_to):
    """Ignora tablas/índices reflejados que NO son del proyecto (p. ej. tablas
    internas de PostGIS: spatial_ref_sys, tiger geocoder, topology). Para lo demás
    delega en el helper de geoalchemy2, que gestiona los índices espaciales."""
    if type_ == "table" and reflected and name not in target_metadata.tables:
        return False
    return alembic_helpers.include_object(obj, name, type_, reflected, compare_to)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        render_item=alembic_helpers.render_item,
        process_revision_directives=alembic_helpers.writer,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            render_item=alembic_helpers.render_item,
            process_revision_directives=alembic_helpers.writer,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
