import pytest


@pytest.fixture(scope="session")
def test_app():
    from blog import create_app

    app = create_app("default")
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()
