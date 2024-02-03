import pytest


@pytest.fixture(scope="module")
def container_setup():
    # issue container build -> run cmd
    assert True
    yield
    # issue container teardown -> cleanup cmd


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


@pytest.fixture
def cleanup_file():
    yield
    fpath = os.path.join(os.getenv("BLOG_PATH"), "test.md")
    if os.path.exists(fpath):
        os.remove(fpath)
    else:
        print(f"The file {fpath} does not exist, something is wrong")
