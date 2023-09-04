import unittest

from blog.cache import SimpleCache


class TestSimpleCache(unittest.TestCase):
    def setUp(self) -> None:
        self.cache_obj = SimpleCache(500, 500)

    def test_basic(self):
        pass
