"""Interfaces de proveedores intercambiables (adaptadores).

El pipeline depende SOLO de estas interfaces, nunca de un proveedor concreto.
Esto permite sustituir Google por OSM/DENUE, o Jooble por otro agregador, sin
reescribir el sistema.

Sin implementación todavía: las clases concretas llegan en Fases 4 (lugares) y 7
(vacantes). Cada método debe devolver datos con su fuente/fecha/confianza cuando
se implemente, y NUNCA inventar datos (ausencia -> None/NULL).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PlaceProvider(ABC):
    """Descubrimiento y detalle de establecimientos (Google Places, OSM, DENUE...)."""

    name: str

    @abstractmethod
    def search_places(
        self, *, lat: float, lng: float, radius_m: int, **kwargs: Any
    ) -> list[dict]:
        """Busca lugares dentro de un radio. Devuelve registros crudos del proveedor."""
        raise NotImplementedError

    @abstractmethod
    def get_place_details(self, provider_place_id: str) -> dict:
        """Detalle de un lugar por su id en el proveedor."""
        raise NotImplementedError


class JobProvider(ABC):
    """Búsqueda de vacantes (Jooble, careers de franquicias...)."""

    name: str

    @abstractmethod
    def search_jobs(
        self, *, keywords: str, location: str, **kwargs: Any
    ) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_job_details(self, job_id: str) -> dict:
        raise NotImplementedError


class SearchProvider(ABC):
    """Búsqueda web genérica (enriquecimiento: web oficial, redes...)."""

    name: str

    @abstractmethod
    def search_web(self, query: str, **kwargs: Any) -> list[dict]:
        raise NotImplementedError


class GeocoderProvider(ABC):
    """Geocodificación directa e inversa."""

    name: str

    @abstractmethod
    def geocode(self, address: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def reverse_geocode(self, lat: float, lng: float) -> dict | None:
        raise NotImplementedError
