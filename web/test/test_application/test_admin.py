import io
import os

from flask import session
import pytest


def test_admin_route_before_request_handler(session_setup, auth_token, monkeypatch):
    """
    - w/o w/ token + login/non login
    - direct logout
    """
    _, test_app = session_setup
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
    assert response.status_code == 401
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

        # to test logout redirects to main.index
        # fail suspect due to context manager works in streaming mode
        response = client.get("/admin/logout", follow_redirects=True)
        assert response.status_code == 200
        assert "token" not in session

    client = test_app.test_client(use_cookies=True)

    with client:
        response = client.post(
            "/admin/login", data={"token": auth_token}, follow_redirects=True
        )
        monkeypatch.setattr("blog.admin.view.verify_token", lambda x: False)
        response = client.get("/admin/fsrs/setup/cards")
        assert response.status_code == 401


def test_upload_with_monkeypatch(session_setup, auth_token, monkeypatch):
    _, test_app = session_setup
    client = test_app.test_client(use_cookies=True)
    monkeypatch.setattr("werkzeug.datastructures.FileStorage.save", lambda x, y: None)

    with client:
        response = client.post(
            "/admin/login", data={"token": auth_token}, follow_redirects=True
        )
        assert response.status_code == 200

        data = {"file": (io.BytesIO(b"abcdef"), "test.md"), "token": auth_token}
        response = client.post(
            "/admin/blog/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert response.status_code == 200

        data_no_file = {"token": auth_token}
        response = client.post(
            "/admin/blog/upload", data=data_no_file, content_type="multipart/form-data"
        )
        assert response.status_code == 400

        data_multi_file = {
            "file": [
                (io.BytesIO(b"abcdef"), "test1.md"),
                (io.BytesIO(b"abcdef"), "test2.md"),
            ],
            "token": auth_token,
        }
        response = client.post(
            "/admin/blog/upload",
            data=data_multi_file,
            content_type="multipart/form-data",
            follow_redirects=True,
        )


@pytest.mark.usefixtures("cleanup_file")
def test_upload_without_monkeypatch(session_setup, auth_token):
    _, test_app = session_setup
    client = test_app.test_client(use_cookies=True)

    with client:
        response = client.post(
            "/admin/login", data={"token": auth_token}, follow_redirects=True
        )
        assert response.status_code == 200

        data = {"file": (io.BytesIO(b"abcdef"), "test.md"), "token": auth_token}
        response = client.post(
            "/admin/blog/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert response.status_code == 200
        with open(os.path.join(os.getenv("BLOG_PATH"), "test.md"), "r") as rf:
            assert rf.read() == "abcdef"
