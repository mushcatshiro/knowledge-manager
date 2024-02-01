import os

from blog.utils import create_fake_data

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import insert


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


@pytest.fixture
def bookmark_db(db):
    from blog.bookmark import BookmarkModel

    fake_data = create_fake_data(BookmarkModel, num=int(os.getenv("FAKE_DATA_NUM")))

    with Session(db) as session:
        session.execute(
            insert(BookmarkModel),
            fake_data,
        )
        session.commit()
    yield db
