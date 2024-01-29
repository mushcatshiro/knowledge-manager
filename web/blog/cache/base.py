class BaseCache:
    def __init__(self, timeout):
        self.default_timeout = timeout

    def get(self, key):
        return None

    def get_many(self, *keys):
        return [self.get(k) for k in keys]

    def delete(self, key):
        return True

    def delete_many(self, *keys):
        deleted_keys = []
        for key in keys:
            if self.delete(key):
                deleted_keys.append(key)
        return deleted_keys

    def set(self, key, value):
        return True

    def set_many(self, map):
        set_keys = []
        for k, v in map.items():
            if self.set(k, v):
                set_keys.append(k)
        return set_keys

    def has(self, key):
        raise NotImplementedError

    def clear(self):
        return True

    def _normalize_timeout(self, timeout):
        if timeout is None:
            timeout = self.default_timeout
        return timeout

    def inc(self, key, delta=1):
        value = (self.get(key) or 0) + delta
        return value if self.set(key, value) else None

    def dec(self, key, delta=1):
        value = (self.get(key) or 0) - delta
        return value if self.set(key, value) else None

    def get_dict(self, *keys):
        return dict(zip(keys, self.get_many(*keys)))
