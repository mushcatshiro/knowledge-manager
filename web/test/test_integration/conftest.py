import os
import pytest


@pytest.fixture(scope="session")
def test_app():
    from blog import create_app

    app = create_app("default")
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture(scope="session")
def auth_token(test_app):
    client = test_app.test_client()
    response = client.post("/auth/authenticate", json={"auth": os.getenv("AUTH")})
    return response.json["token"]
