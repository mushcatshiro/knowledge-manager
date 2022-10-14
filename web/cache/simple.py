from time import time

from .base import BaseCache
from web.utils.sync import RWLock


class SimpleCache(BaseCache):
    """
    fork of pallets-eco/cachelib with slight modification
    """
    def __init__(self, timeout, threshold):
        super().__init__(timeout)
        self.cache = {}
        self.threshold = threshold
        self.lock = RWLock()
        self.serializer = None  # TODO not sure if needed

    def _remove(self, now=None):
        if now:
            with self.lock.r_locked():
                toremove = [
                    k for k, (expires, _) in self.cache.items()
                    if expires < now()
                ]
            with self.lock.w_locked():
                for k in toremove:
                    self.cache.pop(k, None)
        else:
            with self.lock.r_locked():
                k_ordered = (
                    k for k, v in sorted(
                        self.cache.items(), key=lambda item: item[1][0]
                    )
                )
            with self.lock.w_locked():
                for k in k_ordered:
                    self.cache.pop(k, None)
                    if not len(self.cache) > self.threshold:
                        break

    def _prune(self):
        if len(self.cache) > self.threshold:
            now = time()
            self._remove(now)
        if len(self.cache) > self.threshold:
            self._remove()

    def get(self, key):
        try:
            with self.lock.r_locked():
                expires, value = self.cache[key]
            if expires > time():
                return value
            else:
                return None
        except KeyError:
            return None

    def set(self, key, value):
        expires = time() + self.timeout
        with self.lock.w_locked():
            self._prune()
            self.cache[key] = (expires, value)
        return True

    def delete(self, key):
        with self.lock.w_locked():
            ret = self.cache.pop(key, None)
        return ret

    def has(self, key):
        with self.lock.r_locked():
            try:
                expires, _ = self.cache[key]
                return bool(expires > time())
            except KeyError:
                return False

    def clear(self):
        with self.lock.w_locked():
            self.cache.clear()
        return not bool(self.cache)


class SimpleLRUCache(BaseCache):
    pass