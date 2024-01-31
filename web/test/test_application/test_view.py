import os

from blog.core.crud import CRUDBase


def test_main_route_blog(test_app, monkeypatch, bookmark_db):
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
    expected_length = os.getenv("FAKE_DATA_NUM")
    more_than_1_page = int(expected_length) > int(os.getenv("PAGINATION_LIMIT"))

    client = test_app.test_client()
    response = client.get("/bookmarklet-list")
    assert response.status_code == 200
    assert (
        b'<a class="nav-link active" href="/bookmarklet-list">Reading List</a>'
        in response.data
    )
    assert (
        b'style="pointer-events: none; color: darkgray"\n  >\n  &laquo;'
        in response.data
    )
    if more_than_1_page:
        assert (
            len(response.data.decode("utf-8").split("<li>"))
            == int(os.getenv("PAGINATION_LIMIT")) + 1
        )
        assert b'href="/bookmarklet-list?page=2"' in response.data

        response = client.get("bookmarklet-list?page=2")
        assert response.status_code == 200
        assert (
            b'<a class="nav-link active" href="/bookmarklet-list">Reading List</a>'
            in response.data
        )
    else:
        assert (
            len(response.data.decode("utf-8").split("<li>")) == int(expected_length) + 1
        )
        assert (
            b'style="pointer-events: none; color: darkgray"\n  >\n  &raquo;'
            in response.data
        )


def test_main_route_secured(test_app):
    pass
