from blog.utils import paginate
from blog.bookmark import BookmarkModel
from blog.core.crud import CRUDBase


def test_paginate_function(session_setup, bookmark_db_fixture):
    _, test_app = session_setup
    bookmark_db, FAKE_DATA_NUM = bookmark_db_fixture
    basecrud = CRUDBase(BookmarkModel, bookmark_db)
    rv = paginate(1, basecrud, 10)
    assert len(rv["instances"]) == 10
    assert rv["total"] == FAKE_DATA_NUM
    assert not rv["has_prev"]
    assert rv["has_next"]
    assert rv["next_num"] == 2
    assert rv["prev_num"] is None

    rv = paginate(2, basecrud, 10)
    assert len(rv["instances"]) == 10
    assert rv["total"] == FAKE_DATA_NUM
    assert rv["has_prev"]
    assert rv["has_next"]
    assert rv["next_num"] == 3
    assert rv["prev_num"] == 1

    rv = paginate(3, basecrud, 10)
    assert len(rv["instances"]) == 10
    assert rv["total"] == FAKE_DATA_NUM
    assert rv["has_prev"]
    assert rv["has_next"]
    assert rv["next_num"] == 4
    assert rv["prev_num"] == 2

    rv = paginate(4, basecrud, 10)
    assert len(rv["instances"]) == 10
    assert rv["total"] == FAKE_DATA_NUM
    assert rv["has_prev"]
    assert not rv["has_next"]
    assert rv["next_num"] is None
    assert rv["prev_num"] == 3
