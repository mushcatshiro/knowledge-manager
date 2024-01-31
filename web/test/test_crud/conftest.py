import os

from blog.utils import create_fake_data

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import insert


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


@pytest.fixture
def negotium_db(db):
    from blog.negotium import NegotiumModel

    fake_data = create_fake_data(
        NegotiumModel, num=int(os.getenv("FAKE_DATA_NUM")) // 4, max_int=10
    )

    with Session(db) as session:
        session.execute(
            insert(NegotiumModel),
            fake_data,
        )
        session.commit()
    yield db
