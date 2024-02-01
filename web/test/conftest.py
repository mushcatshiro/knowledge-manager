import os

import pytest
from sqlalchemy import create_engine

from blog import Base
from blog.utils import set_env_var


def pytest_sessionstart(session):
    config = session.config  # noqa remove?
    set_env_var(fname=".env.test")


@pytest.fixture(scope="session")
def db():
    engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"), echo=False)
    Base.metadata.create_all(engine)

    yield engine
    os.remove(os.getenv("SQLALCHEMY_DATABASE_NAME"))
