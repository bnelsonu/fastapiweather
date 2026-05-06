import asyncio
import random
from time import monotonic

import httpx

BASE_URL = "https://api.open-meteo.com/v1/forecast"
_CACHE_TTL_SECONDS = 15
_MAX_RETRIES = 2
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

_client = httpx.AsyncClient(
    timeout=10.0,
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
)
_request_semaphore = asyncio.Semaphore(20)
_cache_lock = asyncio.Lock()
_cache: dict[tuple[float, float], tuple[float, dict]] = {}


async def _get_cached_weather(key: tuple[float, float]) -> dict | None:
    async with _cache_lock:
        cached = _cache.get(key)
        if not cached:
            return None

        expires_at, payload = cached
        if monotonic() >= expires_at:
            _cache.pop(key, None)
            return None

        return payload


async def _set_cached_weather(key: tuple[float, float], payload: dict) -> None:
    async with _cache_lock:
        _cache[key] = (monotonic() + _CACHE_TTL_SECONDS, payload)


async def fetch_weather(lat: float, lon: float):
    key = (round(lat, 4), round(lon, 4))

    cached_payload = await _get_cached_weather(key)
    if cached_payload is not None:
        return cached_payload

    async with _request_semaphore:
        # Re-check cache after waiting for the semaphore; another request may have filled it.
        cached_payload = await _get_cached_weather(key)
        if cached_payload is not None:
            return cached_payload

        for attempt in range(_MAX_RETRIES + 1):
            try:
                response = await _client.get(
                    BASE_URL,
                    params={"latitude": lat, "longitude": lon, "current_weather": True},
                )

                if response.status_code in _RETRYABLE_STATUS_CODES:
                    if attempt < _MAX_RETRIES:
                        await asyncio.sleep(
                            (0.2 * (2**attempt)) + random.uniform(0, 0.1)
                        )
                        continue

                response.raise_for_status()
                payload = response.json()
                await _set_cached_weather(key, payload)
                return payload

            except httpx.RequestError:
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep((0.2 * (2**attempt)) + random.uniform(0, 0.1))
                    continue
                raise
