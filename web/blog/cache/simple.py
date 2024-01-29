import logging
import pickle
import time

from .base import BaseCache


logger = logging.getLogger(__name__)


class SimpleSerializer:
    def _warn(self, e: pickle.PickleError) -> None:
        logger.warning(f"An exception has been raised during a pickling operation: {e}")

    def dumps(self, value, protocol=pickle.HIGHEST_PROTOCOL):
        try:
            serialized = pickle.dumps(value, protocol)
        except (pickle.PickleError, pickle.PicklingError) as e:
            self._warn(e)
        return serialized

    def loads(self, bvalue):
        try:
            data = pickle.loads(bvalue)
        except pickle.PickleError as e:
            self._warn(e)
            return None
        else:
            return data


class SimpleCache(BaseCache):

    """Simple memory cache for single process environments.  This class exists
    mainly for the development server and is not 100% thread safe.  It tries
    to use as many atomic operations as possible and no locks for simplicity
    but it could happen under heavy load that keys are added multiple times.

    :param threshold: the maximum number of items the cache stores before
                      it starts deleting some.
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`. A timeout of
                            0 indicates that the cache never expires.
    """

    serializer = SimpleSerializer()

    def __init__(
        self,
        threshold=500,
        default_timeout=300,
    ):
        BaseCache.__init__(self, default_timeout)
        self._cache = {}
        self._threshold = threshold or 500  # threshold = 0

    def _over_threshold(self):
        return len(self._cache) > self._threshold

    def _remove_expired(self, now):
        toremove = [k for k, (expires, _) in self._cache.items() if expires < now]
        for k in toremove:
            self._cache.pop(k, None)

    def _remove_older(self):
        k_ordered = (
            k
            for k, v in sorted(
                self._cache.items(), key=lambda item: item[1][0]  # type: ignore
            )
        )
        for k in k_ordered:
            self._cache.pop(k, None)
            if not self._over_threshold():
                break

    def _prune(self):
        if self._over_threshold():
            now = time.time()
            self._remove_expired(now)
        # remove older items if still over threshold
        if self._over_threshold():
            self._remove_older()

    def _normalize_timeout(self, timeout):
        timeout = BaseCache._normalize_timeout(self, timeout)
        if timeout > 0:
            timeout = int(time.time()) + timeout
        return timeout

    def get(self, key):
        try:
            expires, value = self._cache[key]
            if expires == 0 or expires > time.time():
                return self.serializer.loads(value)
        except KeyError:
            return None

    def set(self, key, value, timeout=None):
        expires = self._normalize_timeout(timeout)
        self._prune()
        self._cache[key] = (expires, self.serializer.dumps(value))
        return True

    def add(self, key, value, timeout=None):
        expires = self._normalize_timeout(timeout)
        self._prune()
        item = (expires, self.serializer.dumps(value))
        if key in self._cache:
            return False
        self._cache.setdefault(key, item)
        return True

    def delete(self, key):
        return self._cache.pop(key, None) is not None

    def has(self, key):
        try:
            expires, value = self._cache[key]
            return bool(expires == 0 or expires > time.time())
        except KeyError:
            return False

    def clear(self):
        self._cache.clear()
        return not bool(self._cache)
