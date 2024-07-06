from unittest import mock


def test_main_route_blog(session_setup, blogpost_db, monkeypatch):
    _, test_app = session_setup
    client = test_app.test_client()

    response = client.get("/blog")
    assert response.status_code == 200
    assert b'<a class="nav-link active" href="/blog">Blog</a>' in response.data

    response = client.get("/blog/does-not-exist")
    assert response.status_code == 200
    assert b"Blog post does-not-exist not found!" in response.data

    monkeypatch.setattr("builtins.open", mock.mock_open(read_data=b"mocked"))

    response = client.get("/blog/test%20title%201")
    assert response.status_code == 200
    assert b"mocked" in response.data


def test_main_route_bookmarklet_list_single_page(session_setup, bookmark_db):
    """
    TODO
    ----
    - use database instead of monkeypatch
    - test empty database/table not created/no instance returned
      - might need to modify crud.py
    """
    _, test_app = session_setup
    expected_length = test_app.config["FAKE_DATA_NUM"]
    assert expected_length == test_app.config["PAGINATION_LIMIT"]

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
    assert len(response.data.decode("utf-8").split("<li>")) == expected_length + 1
    assert (
        b'style="pointer-events: none; color: darkgray"\n  >\n  &raquo;'
        in response.data
    )


def test_main_route_bookmarklet_list_multi_page(session_setup, bookmarks_db):
    _, test_app = session_setup
    expected_length = test_app.config["FAKE_DATA_LARGE_NUM"]
    assert expected_length > test_app.config["PAGINATION_LIMIT"]

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
    assert (
        len(response.data.decode("utf-8").split("<li>"))
        == test_app.config["PAGINATION_LIMIT"] + 1
    )
    assert b'href="/bookmarklet-list?page=2"' in response.data

    response = client.get("bookmarklet-list?page=2")
    assert response.status_code == 200
    assert (
        b'<a class="nav-link active" href="/bookmarklet-list">Reading List</a>'
        in response.data
    )


def test_main_route_secured():
    pass
