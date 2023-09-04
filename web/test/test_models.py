import unittest

from web.blog import create_app, db


class TestModels(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app("default")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        return super().setUp()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        return super().tearDown()

    def _test_create_entry(self):
        rv = self.client.get(
            "/api/bookmark?title=Why+TensorFlow+for+Python+is+dying+a+slow+death&url=https%3A%2F%2Fthenextweb.com%2Fnews%2Fwhy-tensorflow-for-python-is-dying-a-slow-death&desc=Many+developers+who+use+Python+for+machine+learning+are+now+switching+to+PyTorch.+Find+out+why+and+what+the+future+could+hold+for+TensorFlow.&img=https%3A%2F%2Fimg-cdn.tnwcdn.com%2Fimage%2Ftnw%3Ffilter_last%3D1%26fit%3D1280%252C640%26url%3Dhttps%253A%252F%252Fcdn0.tnwcdn.com%252Fwp-content%252Fblogs.dir%252F1%252Ffiles%252F2023%252F01%252FAdd-a-heading-1.jpg%26signature%3D0118422d6dab7f09d89f3c0b7b7e58df&nexturl=https%3A%2F%2Fthenextweb.com%2Fnews%2Fwhy-tensorflow-for-python-is-dying-a-slow-death&token="
        )
        print(rv.get_json())

    def _test_read_entry(self):
        rv = self.client.get("/api/query")
        print(rv.get_json())

    def test_read_entry(self):
        self._test_create_entry()
        self._test_read_entry()

    def test_read_multiple(self):
        pass
