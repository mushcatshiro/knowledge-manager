import os

from flask import session


def test_admin_route_before_request_handler(test_app, auth_token):
    """
    - w/o w/ token + login/non login
    - direct logout
    """
    client = test_app.test_client(use_cookies=True)

    response = client.get("/admin/fsrs/setup/cards")
    assert response.status_code == 302
    assert (
        response.location
        == "/admin/login?next=http%3A%2F%2Flocalhost%2Fadmin%2Ffsrs%2Fsetup%2Fcards"
    )

    response = client.get("/admin/fsrs/setup/cards", data={"token": "invalid"})
    assert response.status_code == 302
    assert (
        response.location
        == "/admin/login?next=http%3A%2F%2Flocalhost%2Fadmin%2Ffsrs%2Fsetup%2Fcards"
    )

    response = client.post("/admin/login", data={"token": "invalid"})
    assert response.status_code == 400
    assert b"Invalid token" in response.data

    with client:
        response = client.post(
            "/admin/login", data={"token": auth_token}, follow_redirects=True
        )
        assert response.status_code == 200
        assert session["token"] == auth_token

        response = client.get("/admin/fsrs/setup/cards")
        assert response.status_code == 200
        assert b"setup cards" in response.data

        response = client.get("/admin/logout", follow_redirects=True)
        assert response.status_code == 200
        assert response.location == "/"
        assert "token" not in session
    
    client = test_app.test_client(use_cookies=True)
