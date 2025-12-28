"""Cache package for travel agent."""

from .redis_cache import (
    cache,
    cached,
    get_cached_places,
    set_cached_places,
    invalidate_places,
    cache_stats,
    places_key,
    routes_key,
)

__all__ = [
    "cache",
    "cached",
    "get_cached_places",
    "set_cached_places",
    "invalidate_places",
    "cache_stats",
    "places_key",
    "routes_key",
]
