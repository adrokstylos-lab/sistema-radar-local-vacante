"""Cliente HTTP compartido: User-Agent, timeout y reintentos con backoff.

Devuelve la respuesta junto con metadatos (latencia, status) para poder
registrarlos en `source_requests` (observabilidad y control de costos).
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from backend.app.core.config import settings
from backend.app.core.logging import get_logger

logger = get_logger("radar.http")

# Reintentar solo ante errores transitorios: problemas de red/timeout o
# respuestas 429 / 5xx (típicas de Overpass bajo carga). Nunca ante 4xx.
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.TransportError, httpx.TimeoutException)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in _RETRYABLE_STATUS
    return False


@dataclass
class HttpResult:
    data: Any
    status_code: int
    latency_ms: int
    url: str


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=20),
    retry=retry_if_exception(_is_retryable),
)
def _request(method: str, url: str, **kwargs: Any) -> httpx.Response:
    timeout = kwargs.pop("timeout", 90.0)
    with httpx.Client(timeout=timeout, headers={"User-Agent": settings.http_user_agent}) as client:
        resp = client.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp


def fetch_json(method: str, url: str, **kwargs: Any) -> HttpResult:
    """Hace una petición y devuelve el JSON + metadatos. Relanza en error."""
    start = time.perf_counter()
    resp = _request(method, url, **kwargs)
    latency_ms = int((time.perf_counter() - start) * 1000)
    logger.info("%s %s -> %s (%d ms)", method, url, resp.status_code, latency_ms)
    return HttpResult(
        data=resp.json(),
        status_code=resp.status_code,
        latency_ms=latency_ms,
        url=str(resp.request.url),
    )
