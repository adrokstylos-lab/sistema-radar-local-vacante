"""Configuración central. Lee variables de entorno / .env (nunca hardcodear secretos)."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Base de datos
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/radar"

    # Claves de proveedores (opcionales hasta Fase 4/7)
    google_places_api_key: str | None = None
    jooble_api_key: str | None = None

    # Proveedores OpenStreetMap (gratis, sin key)
    overpass_url: str = "https://overpass-api.de/api/interpreter"
    nominatim_url: str = "https://nominatim.openstreetmap.org/search"
    # User-Agent identificativo (requerido por la política de uso de Nominatim).
    # No incluir datos personales; ajustar con un contacto propio si se desea.
    http_user_agent: str = "RadarLocalNegocios/0.1 (discovery bot)"

    # Producción
    environment: str = "development"  # development | production
    # Orígenes permitidos para CORS (coma-separados). Vacío = mismo origen (el
    # dashboard lo sirve el propio FastAPI, así que normalmente no hace falta).
    cors_origins: str = ""

    # Logging
    log_level: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
