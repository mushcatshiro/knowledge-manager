from blog.core.crud import CRUDBase


def test_main_route_blog(test_app):
    client = test_app.test_client()
    response = client.get("/blog")
    assert response.status_code == 200
    assert b'<a class="nav-link active" href="/blog">Blog</a>' in response.data


def test_main_route_blog_dne(test_app):
    client = test_app.test_client()
    response = client.get("/blog/does-not-exist")
    assert response.status_code == 200
    assert b"Blog does-not-exist not found!" in response.data


def test_main_route_bookmarklet_list(test_app, monkeypatch):
    def mock_query(*args, **kwargs):
        return MockCrudBase().execute()

    monkeypatch.setattr(CRUDBase, "execute", mock_query)
    client = test_app.test_client()
    response = client.get("/bookmarklet-list")
    assert response.status_code == 200
    assert (
        b'<a class="nav-link active" href="/bookmarklet-list">Reading List</a>'
        in response.data
    )


class MockCrudBase:
    def execute(self):
        return [
            MockBaseModel(),
        ]


class MockBaseModel:
    def __init__(self):
        self.id = 1
        self.title = "test"
        self.url = "http://test.com"
        self.timestamp = "2020-01-01 00:00:00"

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "timestamp": self.timestamp,
        }
