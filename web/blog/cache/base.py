class BaseCache:
    def __init__(self, timeout):
        self.timeout = timeout

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

    def has(self):
        raise NotImplementedError

    def clear(self):
        return True
