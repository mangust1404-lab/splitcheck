import time

import httpx

# In-memory cache: {base_currency: (rates_dict, timestamp)}
_cache: dict[str, tuple[dict[str, float], float]] = {}
CACHE_TTL = 3600  # 1 hour


async def get_exchange_rates(base: str = "USD") -> dict[str, float]:
    """Fetch exchange rates from a free API, with 1-hour cache."""
    now = time.time()
    if base in _cache:
        rates, cached_at = _cache[base]
        if now - cached_at < CACHE_TTL:
            return rates

    url = f"https://open.er-api.com/v6/latest/{base}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    rates = data.get("rates", {})
    _cache[base] = (rates, now)
    return rates
