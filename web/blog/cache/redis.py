import pickle
import logging

import redis

from .base import BaseCache


logger = logging.getLogger(__name__)


class RedisSerializer:
    def _warn(self, e):
        logger.warning(f"An exception has been raised during a pickling operation: {e}")

    def dumps(self, value, protocol=pickle.HIGHEST_PROTOCOL):
        """Dumps an object into a string for redis, using pickle by default."""
        return b"!" + pickle.dumps(value, protocol)

    def loads(self, value):
        """The reversal of :meth:`dump_object`. This might be called with
        None.
        """
        if value is None:
            return None
        if value.startswith(b"!"):
            try:
                return pickle.loads(value[1:])
            except pickle.PickleError:
                return None


class RedisCache(BaseCache):
    """Uses the Redis key-value store as a cache backend.
    Note: Python Redis API already takes care of encoding unicode strings on
    the fly. Any additional keyword arguments will be passed to `redis.Redis`.
    """

    _read_client = None
    _write_client = None
    serializer = RedisSerializer()

    def __init__(
        self,
        host="localhost",
        port=6379,
        password=None,
        db=0,
        default_timeout=300,
        key_prefix=None,
        **kwargs,
    ):
        BaseCache.__init__(self, default_timeout)
        self._write_client = self._read_client = redis.Redis(
            host=host, port=port, password=password, db=db, **kwargs
        )
        self.key_prefix = key_prefix or ""

    def _normalize_timeout(self, timeout):
        """Normalize timeout by setting it to default of 300 if
        not defined (None) or -1 if explicitly set to zero.
        """
        timeout = BaseCache._normalize_timeout(self, timeout)
        if timeout == 0:
            timeout = -1
        return timeout

    def get(self, key):
        return self.serializer.loads(self._read_client.get(self.key_prefix + key))

    def get_many(self, *keys):
        if self.key_prefix:
            prefixed_keys = [self.key_prefix + key for key in keys]
        else:
            prefixed_keys = list(keys)
        return [self.serializer.loads(x) for x in self._read_client.mget(prefixed_keys)]

    def set(self, key, value, timeout=None):
        timeout = self._normalize_timeout(timeout)
        dump = self.serializer.dumps(value)
        if timeout == -1:
            result = self._write_client.set(name=self.key_prefix + key, value=dump)
        else:
            result = self._write_client.setex(
                name=self.key_prefix + key, value=dump, time=timeout
            )
        return result

    def add(self, key, value, timeout=None):
        timeout = self._normalize_timeout(timeout)
        dump = self.serializer.dumps(value)
        created = self._write_client.setnx(name=self.key_prefix + key, value=dump)
        # handle case where timeout is explicitly set to zero
        if created and timeout != -1:
            self._write_client.expire(name=self.key_prefix + key, time=timeout)
        return created

    def set_many(self, mapping, timeout=None):
        timeout = self._normalize_timeout(timeout)
        # Use transaction=False to batch without calling redis MULTI
        # which is not supported by twemproxy
        pipe = self._write_client.pipeline(transaction=False)

        for key, value in mapping.items():
            dump = self.serializer.dumps(value)
            if timeout == -1:
                pipe.set(name=self.key_prefix + key, value=dump)
            else:
                pipe.setex(name=self.key_prefix + key, value=dump, time=timeout)
        results = pipe.execute()
        res = zip(mapping.keys(), results)  # noqa: B905
        return [k for k, was_set in res if was_set]

    def delete(self, key):
        return bool(self._write_client.delete(self.key_prefix + key))

    def delete_many(self, *keys):
        if not keys:
            return []
        if self.key_prefix:
            prefixed_keys = [self.key_prefix + key for key in keys]
        else:
            prefixed_keys = [k for k in keys]
        self._write_client.delete(*prefixed_keys)
        return [k for k in prefixed_keys if not self.has(k)]

    def has(self, key):
        return bool(self._read_client.exists(self.key_prefix + key))

    def clear(self):
        status = 0
        if self.key_prefix:
            keys = self._read_client.keys(self.key_prefix + "*")
            if keys:
                status = self._write_client.delete(*keys)
        else:
            status = self._write_client.flushdb()
        return bool(status)

    def inc(self, key, delta=1):
        return self._write_client.incr(name=self.key_prefix + key, amount=delta)

    def dec(self, key, delta=1):
        return self._write_client.incr(name=self.key_prefix + key, amount=-delta)
