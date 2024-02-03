import time


class TestData:
    """This class centralizes all data samples used in tests"""

    sample_numbers = [0, 10, 1024000, 9, 5000000000000, 99, 738, 2000000]
    sample_pairs = {
        "128": False,
        "beef": True,
        "crevettes": {},
        "1024": "spam",
        "bacon": "eggs",
        "sausage": 2048,
        "3072": [],
        "brandy": [{}, "fried eggs"],
        "lobster": ["baked beans", [512]],
        "4096": {"sauce": [], 256: "truffle"},
    }


class ClearTests(TestData):
    def test_clear(self):
        cache = self.cache_factory()
        assert cache.set_many(self.sample_pairs)
        assert cache.clear()
        assert not any(cache.get_many(*self.sample_pairs))


class HasTests(TestData):
    def test_has(self):
        cache = self.cache_factory()
        assert cache.set_many(self.sample_pairs)
        for k in self.sample_pairs:
            assert cache.has(k)
        assert not cache.has("unknown")


class CommonTests(TestData):
    def test_set_get(self):
        cache = self.cache_factory()
        for k, v in self.sample_pairs.items():
            assert cache.set(k, v)
            assert cache.get(k) == v

    def test_set_get_many(self):
        cache = self.cache_factory()
        result = cache.set_many(self.sample_pairs)
        assert result == list(self.sample_pairs.keys())
        values = cache.get_many(*self.sample_pairs)
        assert values == list(self.sample_pairs.values())

    def test_get_dict(self):
        cache = self.cache_factory()
        cache.set_many(self.sample_pairs)
        d = cache.get_dict(*self.sample_pairs)
        assert d == self.sample_pairs

    def test_delete(self):
        cache = self.cache_factory()
        for k, v in self.sample_pairs.items():
            cache.set(k, v)
            assert cache.delete(k)
            assert not cache.get(k)

    def test_delete_many(self):
        cache = self.cache_factory()
        cache.set_many(self.sample_pairs)
        result = cache.delete_many(*self.sample_pairs)
        assert result == list(self.sample_pairs.keys())
        assert not any(cache.get_many(*self.sample_pairs))

    def test_delete_many_ignore_errors(self):
        cache = self.cache_factory()
        cache.set("bacon", "spam")
        cache.delete_many("eggs", "bacon")
        assert cache.get("bacon") is None

    def test_add(self):
        cache = self.cache_factory()
        cache.set_many(self.sample_pairs)
        for k in self.sample_pairs:
            assert not cache.add(k, "updated")
        assert cache.get_many(*self.sample_pairs) == list(self.sample_pairs.values())
        for k, v in self.sample_pairs.items():
            assert cache.add(f"{k}-new", v)
            assert cache.get(f"{k}-new") == v

    def test_inc_dec(self):
        cache = self.cache_factory()
        for n in self.sample_numbers:
            assert not cache.get(f"{n}-key-inc")
            assert cache.inc(f"{n}-key-inc", n) == n
            assert cache.get(f"{n}-key-inc") == n
            assert cache.dec(f"{n}-key-dec", n) == -n
            assert cache.get(f"{n}-key-dec") == -n
            assert cache.dec(f"{n}-key-inc", 5) == n - 5

    def test_expiration(self):
        cache = self.cache_factory()
        for k, v in self.sample_pairs.items():
            cache.set(f"{k}-t0", v, timeout=0)
            cache.set(f"{k}-t1", v, timeout=1)
        time.sleep(4)
        for k, v in self.sample_pairs.items():
            assert cache.get(f"{k}-t0") == v
            assert not cache.get(f"{k}-t1")
