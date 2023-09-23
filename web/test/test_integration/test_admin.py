import os


def test_admin_route_before_request_handler(test_app):
    client = test_app.test_client(use_cookies=True)
    response = client.get("/admin/fsrs/setup/cards")
    assert response.status_code == 302
    assert (
        response.location
        == "/admin/login?next=http%3A%2F%2Flocalhost%2Fadmin%2Ffsrs%2Fsetup%2Fcards"
    )


def test_admin_invalid_token(test_app):
    client = test_app.test_client(use_cookies=True)
    response = client.post("/admin/login", data={"token": "invalid"})
    assert response.status_code == 400
    assert b"Invalid token" in response.data


def test_admin_invalidate_session(test_app, auth_token):
    """
    TODO
    ----
    add logout to clear session
    """
    client = test_app.test_client(use_cookies=True)
    response = client.post(
        "/admin/login", data={"token": auth_token}, follow_redirects=True
    )
    assert response.status_code == 200
    response = client.get("/admin/fsrs/setup/cards")
    assert response.status_code == 200
    response = client.get("/about")
    response = client.get("/admin/fsrs/setup/cards")
    assert response.status_code == 302
