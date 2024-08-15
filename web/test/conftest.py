import os

from blog.utils import create_fake_data

import pytest
from sqlalchemy import create_engine, delete, insert
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def session_setup():
    from blog.utils import set_env_var

    set_env_var()
    from blog import Base, create_app

    app = create_app("testing")
    ctx = app.app_context()
    ctx.push()

    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=False)
    Base.metadata.create_all(engine)

    yield (engine, app)

    os.remove(app.config["SQLALCHEMY_DATABASE_NAME"])
    ctx.pop()


@pytest.fixture
def bookmark_db_fixture(session_setup):
    engine, test_app = session_setup
    from blog.bookmark import BookmarkModel

    FAKE_DATA_NUM = 40
    fake_data = create_fake_data(BookmarkModel, num=FAKE_DATA_NUM)

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
    yield engine, FAKE_DATA_NUM

    with Session(engine) as session:
        session.execute(delete(BookmarkModel))
        session.commit()


@pytest.fixture
def bookmarks_db_fixture(session_setup):
    engine, test_app = session_setup
    from blog.bookmark import BookmarkModel

    FAKE_DATA_LARGE_NUM = 80
    fake_data = create_fake_data(BookmarkModel, num=FAKE_DATA_LARGE_NUM)

    with Session(engine) as session:
        session.execute(
            insert(BookmarkModel),
            fake_data,
        )
        session.commit()
    yield engine, FAKE_DATA_LARGE_NUM

    with Session(engine) as session:
        session.execute(delete(BookmarkModel))
        session.commit()


@pytest.fixture
def blogpost_db(session_setup):
    """
    BUG
    ```
    fake_data = [
        {"title": "test title 1"},
        {"title": "test title -1", "version": 1},
        {"title": "test title -1", "version": 2, "deleted": 1},
    ]
    with Session(db) as session:
        session.execute(
            insert(BlogPostModel),
            fake_data,
        )
    ```
    does not work for some reason
    """
    engine, _ = session_setup
    from blog.blogpost import BlogPostModel

    instance_1 = BlogPostModel(title="test title 1")
    instance_2 = BlogPostModel(title="test title -1", version=1, deleted=1)
    instance_3 = BlogPostModel(title="test title -1", version=2, deleted=1)
    instance_4 = BlogPostModel(title="test title 0")
    instance_5 = BlogPostModel(title="test title 0", version=2)

    with Session(engine) as session:
        session.add_all([instance_1, instance_2, instance_3, instance_4, instance_5])
        session.commit()
    yield engine

    with Session(engine) as session:
        session.execute(delete(BlogPostModel))
        session.commit()


@pytest.fixture
def blogpost_db_cleanup(session_setup):
    engine, _ = session_setup
    from blog.blogpost import BlogPostModel

    yield

    with Session(engine) as session:
        session.execute(delete(BlogPostModel))
        session.commit()


@pytest.fixture
def negotium_db(session_setup):
    engine, test_app = session_setup
    from blog.negotium import NegotiumModel

    total = 10
    fake_data = create_fake_data(NegotiumModel, num=total, max_int=total)

    with Session(engine) as session:
        session.execute(delete(NegotiumModel))
        session.commit()
        session.execute(
            insert(NegotiumModel),
            fake_data,
        )
        session.commit()
    yield engine, total

    with Session(engine) as session:
        session.execute(delete(NegotiumModel))
        session.commit()
