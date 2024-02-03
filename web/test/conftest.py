import os

import pytest
from sqlalchemy import create_engine


@pytest.fixture(scope="session")
def session_setup():
    from blog import Base, create_app

    app = create_app("testing")
    ctx = app.app_context()
    ctx.push()

    engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI"), echo=False)
    Base.metadata.create_all(engine)

    yield (engine, app)

    os.remove(os.getenv("SQLALCHEMY_DATABASE_NAME"))
    ctx.pop()
