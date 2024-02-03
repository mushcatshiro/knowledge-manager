import os

from blog.utils import create_fake_data

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import insert


@pytest.fixture
def bookmark_db(session_setup):
    engine, test_app = session_setup
    from blog.bookmark import BookmarkModel

    fake_data = create_fake_data(BookmarkModel, num=test_app.config["FAKE_DATA_NUM"])

    with Session(engine) as session:
        session.execute(
            insert(BookmarkModel),
            fake_data,
        )
        session.commit()
    yield engine


@pytest.fixture
def negotium_db(session_setup):
    engine, test_app = session_setup
    from blog.negotium import NegotiumModel

    fake_data = create_fake_data(
        NegotiumModel, num=test_app.config["FAKE_DATA_NUM"] // 4, max_int=10
    )

    with Session(engine) as session:
        session.execute(
            insert(NegotiumModel),
            fake_data,
        )
        session.commit()
    yield engine
