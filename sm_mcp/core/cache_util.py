"""Utility module providing a simple timed LRU cache."""

import time
from typing import Any
from collections import OrderedDict

class TimedCache:
    """A lightweight LRU cache where items expire after ``ttl_seconds``."""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 300) -> None:
        self.max_size = max_size
        self.ttl = ttl_seconds
        # ``_store`` maps keys to ``(expiry_timestamp, value)`` tuples.
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def get(self, key: str) -> Any | None:
        """Return a cached value if present and not expired."""

        now = time.time()
        if key in self._store:
            expiry, value = self._store[key]
            if now < expiry:
                # Move to end to mark as recently used
                self._store.move_to_end(key)
                return value
            # Entry expired -> remove it
            del self._store[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Insert ``value`` into the cache under ``key``."""

        now = time.time()
        self._store[key] = (now + self.ttl, value)
        self._store.move_to_end(key)
        # Remove least recently used item when exceeding ``max_size``
        if len(self._store) > self.max_size:
            self._store.popitem(last=False)

    def clear(self) -> None:
        """Remove all cached entries."""

        self._store.clear()


# Global instance for SiteMinder object detail caching.  These values can be
# tuned as needed by the application.
object_detail_cache = TimedCache(max_size=200, ttl_seconds=600)
