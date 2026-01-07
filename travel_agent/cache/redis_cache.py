"""
REDIS CACHE - Caching for Expensive API Calls
=============================================
Cache Google Places API results to:
1. Reduce API costs
2. Speed up repeated requests
3. Enable faster refinements (user asks to "add more museums")

CACHE KEYS:
- places:{location}:{type} → list of places
- routes:{from_hash}:{to_hash} → travel time

TTL: 24 hours (places data doesn't change that fast)
"""

import os
import json
import hashlib
import logging
from typing import Optional, Any
from functools import wraps

logger = logging.getLogger(__name__)

# Try to import Redis, fallback to in-memory cache
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not installed. Using in-memory cache (not persistent).")


class CacheBackend:
    """Abstract cache backend."""
    
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: int = 86400) -> bool:
        raise NotImplementedError
    
    def delete(self, key: str) -> bool:
        raise NotImplementedError


class RedisCache(CacheBackend):
    """Redis-backed cache."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            decode_responses=True,
            socket_timeout=3,
            socket_connect_timeout=3
        )
        self.connected = False
        # Test connection
        try:
            self.client.ping()
            self.connected = True
            logger.info(f"Redis connected: {host}:{port}")
        except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
            self.connected = False
            logger.warning(f"Redis connection failed: {host}:{port} - {e}")
    
    def get(self, key: str) -> Optional[Any]:
        if not self.connected:
            return None
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 86400) -> bool:
        if not self.connected:
            return False
        try:
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        if not self.connected:
            return False
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

class RedisUrlCache(CacheBackend):
    """Redis-backed cache using URL connection string."""
    
    def __init__(self, url: str):
        # Add timeout to prevent blocking on unreachable Redis
        self.client = redis.from_url(
            url, 
            decode_responses=True,
            socket_timeout=3,  # 3 second timeout for operations
            socket_connect_timeout=3  # 3 second timeout for connection
        )
        self.connected = False
        # Test connection
        try:
            self.client.ping()
            self.connected = True
            logger.info(f"Redis connected via URL")
        except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
            self.connected = False
            logger.warning(f"Redis URL connection failed: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        if not self.connected:
            return None
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 86400) -> bool:
        if not self.connected:
            return False
        try:
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        if not self.connected:
            return False
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False


class InMemoryCache(CacheBackend):
    """In-memory cache fallback (not persistent across restarts)."""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
        logger.info("Using in-memory cache")
    
    def get(self, key: str) -> Optional[Any]:
        import time
        if key in self._cache:
            if key in self._expiry and time.time() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 86400) -> bool:
        import time
        self._cache[key] = value
        self._expiry[key] = time.time() + ttl
        return True
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return True
        return False


# Initialize the cache
def get_cache() -> CacheBackend:
    """Get the appropriate cache backend."""
    redis_url = os.getenv("REDIS_URL")
    
    if REDIS_AVAILABLE and redis_url:
        # Check if it's a full URL (redis://...) or just a hostname
        if redis_url.startswith("redis://") or redis_url.startswith("rediss://"):
            try:
                cache = RedisUrlCache(redis_url)
                if cache.connected:
                    return cache
            except Exception as e:
                logger.warning(f"Redis URL connection failed: {e}")
        else:
            # Treat as hostname
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            cache = RedisCache(host=redis_url, port=redis_port)
            if cache.connected:
                return cache
    
    return InMemoryCache()


# Global cache instance
_cache: Optional[CacheBackend] = None


def cache() -> CacheBackend:
    """Get the global cache instance."""
    global _cache
    if _cache is None:
        _cache = get_cache()
    return _cache


# ============================================================
# CACHE KEY HELPERS
# ============================================================

def cache_key(prefix: str, **kwargs) -> str:
    """Generate a cache key from prefix and kwargs."""
    # Sort for consistent ordering
    sorted_items = sorted(kwargs.items())
    key_str = json.dumps(sorted_items)
    hash_val = hashlib.md5(key_str.encode()).hexdigest()[:12]
    return f"{prefix}:{hash_val}"


def places_key(location: str, place_type: str) -> str:
    """Cache key for places search."""
    return cache_key("places", location=location.lower(), type=place_type.lower())


def routes_key(origin: str, destination: str) -> str:
    """Cache key for route matrix."""
    return cache_key("routes", origin=origin.lower(), destination=destination.lower())


# ============================================================
# CACHING DECORATOR
# ============================================================

def cached(prefix: str, ttl: int = 86400):
    """
    Decorator to cache function results.
    
    Usage:
        @cached("places", ttl=86400)
        def find_places(location: str, type: str) -> dict:
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from function name and arguments
            key = cache_key(prefix, func=func.__name__, args=str(args), kwargs=str(kwargs))
            
            # Try to get from cache
            cached_result = cache().get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache().set(key, result, ttl)
                logger.debug(f"Cache set: {key}")
            
            return result
        return wrapper
    return decorator


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_cached_places(location: str, place_type: str) -> Optional[list]:
    """Get cached places results."""
    key = places_key(location, place_type)
    return cache().get(key)


def set_cached_places(location: str, place_type: str, places: list, ttl: int = 86400) -> bool:
    """Cache places results."""
    key = places_key(location, place_type)
    return cache().set(key, places, ttl)


def invalidate_places(location: str, place_type: str) -> bool:
    """Invalidate cached places (e.g., if user wants fresh results)."""
    key = places_key(location, place_type)
    return cache().delete(key)


def cache_stats() -> dict:
    """Get cache statistics (for monitoring)."""
    c = cache()
    if isinstance(c, InMemoryCache):
        return {
            "backend": "in_memory",
            "entries": len(c._cache)
        }
    elif isinstance(c, RedisCache):
        if c.connected:
            info = c.client.info("memory")
            return {
                "backend": "redis",
                "connected": True,
                "used_memory": info.get("used_memory_human", "unknown")
            }
    return {"backend": "unknown"}
