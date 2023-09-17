def test_main_route_blog(test_app):
    client = test_app.test_client()
    response = client.get("/blog")
    assert response.status_code == 200
    assert b"<a class=\"nav-link active\" href=\"/blog\">Blog</a>" in response.data


def test_main_route_blog_dne(test_app):
    client = test_app.test_client()
    response = client.get("/blog/does-not-exist")
    assert response.status_code == 200
    assert b"Blog does-not-exist not found!" in response.data


def test_main_route_bookmarklet_list(test_app):
    client = test_app.test_client()
    response = client.get("/bookmarklet-list")
    assert response.status_code == 200
    assert b"<a class=\"nav-link\" href=\"/bookmarklet-list\">Bookmarklet List</a>" in response.data