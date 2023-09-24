import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import insert

from blog.bookmark import BookmarkModel
from blog.core.crud import Base
from blog.utils import set_env_var


def pytest_sessionstart(session):
    config = session.config  # noqa remove?
    set_env_var(fname=".env.test")


@pytest.fixture(scope="session")
def db():
    engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"), echo=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.execute(
            insert(BookmarkModel),
            [
                {
                    "title": "test",
                    "url": "http://test.com",
                    "img": "http://test.com/img",
                    "desc": "test",
                },
                {
                    "title": "test2",
                    "url": "http://test2.com",
                    "img": "http://test2.com/img",
                    "desc": "test2",
                },
                {
                    "title": "test3",
                    "url": "http://test3.com",
                    "img": "http://test3.com/img",
                    "desc": "test3",
                },
            ],
        )
        session.commit()
    yield engine
    os.remove(os.getenv("SQLALCHEMY_DATABASE_NAME"))
