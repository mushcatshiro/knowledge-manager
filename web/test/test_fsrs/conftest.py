import os

import pytest
from sqlalchemy import create_engine

from blog.fsrs.model import CardModel
from blog.core.crud import CRUDBase, Base


@pytest.fixture(scope="session")
def db():
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(engine)
    cb = CRUDBase(CardModel, engine)
    instance = cb.execute(
        operation="create",
    )
    yield instance, engine
    os.remove("./test.db")
