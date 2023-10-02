from blog.core.crud import CRUDBase


def test_main_route_blog(test_app, monkeypatch, db):
    def mock_blog_list(*args, **kwargs):
        return ["test1", "test2", "test3"]

    monkeypatch.setattr("os.listdir", mock_blog_list)
    client = test_app.test_client()
    response = client.get("/blog")
    assert response.status_code == 200
    assert b'<a class="nav-link active" href="/blog">Blog</a>' in response.data

    client = test_app.test_client()
    response = client.get("/blog/does-not-exist")
    assert response.status_code == 200
    assert b"Blog does-not-exist not found!" in response.data


def test_main_route_bookmarklet_list(test_app, monkeypatch):
    """
    TODO
    ----
    - use database instead of monkeypatch
    - test empty database/table not created/no instance returned
      - might need to modify crud.py
    """
    client = test_app.test_client()
    response = client.get("/bookmarklet-list")
    assert response.status_code == 200
    assert (
        b'<a class="nav-link active" href="/bookmarklet-list">Reading List</a>'
        in response.data
    )


def test_main_route_secured(test_app):
    pass
