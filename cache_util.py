import time
from typing import Any
from collections import OrderedDict

class TimedCache:
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def get(self, key: str) -> Any | None:
        now = time.time()
        if key in self._store:
            expiry, value = self._store[key]
            if now < expiry:
                # Move to end to mark as recently used
                self._store.move_to_end(key)
                return value
            else:
                del self._store[key]  # Expired
        return None

    def set(self, key: str, value: Any):
        now = time.time()
        self._store[key] = (now + self.ttl, value)
        self._store.move_to_end(key)
        if len(self._store) > self.max_size:
            self._store.popitem(last=False)

    def clear(self):
        self._store.clear()


# Global instance for SiteMinder object detail caching
object_detail_cache = TimedCache(max_size=200, ttl_seconds=600)  # configurable
