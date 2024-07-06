import os

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import insert, delete


@pytest.fixture(scope="session")
def auth_token(session_setup):
    _, test_app = session_setup
    client = test_app.test_client()
    response = client.post("/auth/authenticate", json={"auth": test_app.config["AUTH"]})
    return response.json["token"]


@pytest.fixture
def cleanup_file(session_setup):
    _, test_app = session_setup
    yield
    fpath = os.path.join(test_app.config["BLOG_PATH"], "test.md")
    if os.path.exists(fpath):
        os.remove(fpath)
    else:
        print(f"The file {fpath} does not exist, something is wrong")


@pytest.fixture
def bookmark_db(session_setup):
    engine, test_app = session_setup
    from blog.bookmark import BookmarkModel
    from blog.utils import create_fake_data

    fake_data = create_fake_data(
        BookmarkModel, num=int(test_app.config["FAKE_DATA_NUM"])
    )

    with Session(engine) as session:
        # drop to ensure exactly the number of fake data is inserted
        # depending on execution sequence test\test_application\test_api.py inserts data
        session.execute(delete(BookmarkModel))
        session.commit()
        session.execute(
            insert(BookmarkModel),
            fake_data,
        )
        session.commit()
    yield engine

    with Session(engine) as session:
        session.execute(delete(BookmarkModel))
        session.commit()


@pytest.fixture
def bookmarks_db(session_setup):
    engine, test_app = session_setup
    from blog.bookmark import BookmarkModel
    from blog.utils import create_fake_data

    fake_data = create_fake_data(
        BookmarkModel, num=int(test_app.config["FAKE_DATA_LARGE_NUM"])
    )

    with Session(engine) as session:
        session.execute(
            insert(BookmarkModel),
            fake_data,
        )
        session.commit()
    yield engine

    with Session(engine) as session:
        session.execute(delete(BookmarkModel))
        session.commit()
