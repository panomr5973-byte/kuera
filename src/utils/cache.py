"""KUERA AI — Lightweight TTL Cache Utility.

Simple time-to-live caching for frequently-computed, rarely-changing data.
Not a distributed cache — single-process only.
"""

import time
import hashlib
import json
from typing import Any, Callable, Dict, Optional
from functools import wraps


class _TTLCache:
    """Internal TTL cache store."""

    def __init__(self):
        self._store: Dict[str, tuple] = {}  # key -> (value, expiry_timestamp)

    def get(self, key: str) -> Any:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expiry = entry
        if time.time() > expiry:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        self._store[key] = (value, time.time() + ttl_seconds)

    def clear(self):
        self._store.clear()

    def stats(self) -> Dict[str, int]:
        return {"entries": len(self._store)}


# Global cache instance
_CACHE = _TTLCache()


def ttl_cache(ttl_seconds: int = 300, key_func: Optional[Callable] = None):
    """Decorator that caches function results with TTL.

    Args:
        ttl_seconds: Time-to-live in seconds (default 5 minutes)
        key_func: Optional callable that receives *args, **kwargs and returns a string cache key.
                  Defaults to hashing repr(args) + repr(kwargs).
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = _make_key(func.__name__, args, kwargs)

            cached = _CACHE.get(cache_key)
            if cached is not None:
                return cached

            result = func(*args, **kwargs)
            _CACHE.set(cache_key, result, ttl_seconds)
            return result

        # Attach cache control methods
        wrapper.cache_clear = lambda: _CACHE.clear()
        wrapper.cache_stats = lambda: _CACHE.stats()
        return wrapper

    return decorator


def _make_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Create a deterministic cache key from function arguments."""
    try:
        payload = f"{func_name}:{json.dumps(args, sort_keys=True, default=str)}:{json.dumps(kwargs, sort_keys=True, default=str)}"
    except (TypeError, ValueError):
        payload = f"{func_name}:{repr(args)}:{repr(kwargs)}"
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def cache_clear():
    """Clear all entries from the global TTL cache."""
    _CACHE.clear()


def cache_stats() -> Dict[str, int]:
    """Return cache statistics."""
    return _CACHE.stats()
