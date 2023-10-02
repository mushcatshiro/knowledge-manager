import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import insert

from blog.bookmark import BookmarkModel
from blog.core.crud import Base
from blog.utils import set_env_var, create_fake_data


def pytest_sessionstart(session):
    config = session.config  # noqa remove?
    set_env_var(fname=".env.test")


@pytest.fixture(scope="session")
def db():
    engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"), echo=True)
    Base.metadata.create_all(engine)
    fake_data = create_fake_data(BookmarkModel, num=int(os.getenv("FAKE_DATA_NUM")))
    with Session(engine) as session:
        session.execute(
            insert(BookmarkModel),
            fake_data,
        )
        session.commit()
    yield engine
    os.remove(os.getenv("SQLALCHEMY_DATABASE_NAME"))
