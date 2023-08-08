import pytest
from sqlalchemy import create_engine
import os

from blog.models import Base

@pytest.fixture(scope='session')
def db():
    engine = create_engine('sqlite:///./test.db', echo=True)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()
    os.remove('./test.db')
