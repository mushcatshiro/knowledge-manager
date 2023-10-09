import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import insert

from blog.bookmark import BookmarkModel
from blog.negotium import NegotiumModel
from blog import Base
from blog.utils import set_env_var, create_fake_data


def pytest_sessionstart(session):
    config = session.config  # noqa remove?
    set_env_var(fname=".env.test")


@pytest.fixture(scope="session")
def db():
    engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"), echo=True)
    Base.metadata.create_all(engine)
    bookmark_fake_data = create_fake_data(
        BookmarkModel, num=int(os.getenv("FAKE_DATA_NUM"))
    )
    negotium_fake_data = create_fake_data(
        NegotiumModel, num=int(os.getenv("FAKE_DATA_NUM")) // 4, max_int=10
    )
    with Session(engine) as session:
        session.execute(
            insert(BookmarkModel),
            bookmark_fake_data,
        )
        session.commit()
        session.execute(
            insert(NegotiumModel),
            negotium_fake_data,
        )
        session.commit()
    yield engine
    os.remove(os.getenv("SQLALCHEMY_DATABASE_NAME"))
