import os

from blog.core.crud import CRUDBase
from blog.bookmark import BookmarkModel
from blog.utils import create_fake_data


def test_create(bookmark_db):
    expected_id = int(os.getenv("FAKE_DATA_NUM")) + 1
    fake_data = create_fake_data(BookmarkModel, num=1)

    basecrud = CRUDBase(BookmarkModel, bookmark_db)
    instance = basecrud.safe_execute(
        operation="create",
        **fake_data[0],
    )
    assert instance["id"] == expected_id
    # query the inserted object
    instance = basecrud.safe_execute(operation="get", id=expected_id)
    assert instance["id"] == expected_id
    instance = basecrud.safe_execute(
        operation="create",
        **fake_data[0],
    )
    assert instance is None


def test_update(bookmark_db):
    basecrud = CRUDBase(BookmarkModel, bookmark_db)
    # update the entry with id = 1
    instance = basecrud.safe_execute(
        operation="update",
        id=1,
        title="test_update",
        url="http://test_update.com",
        img="http://test_update.com/img",
        desc="test_update",
    )
    assert instance["id"] == 1
    # query the updated entry
    instance = basecrud.safe_execute(operation="get", id=1)
    assert instance["id"] == 1
    assert instance["title"] == "test_update"
    assert instance["url"] == "http://test_update.com"
    assert instance["img"] == "http://test_update.com/img"
    assert instance["desc"] == "test_update"


def test_get_all(bookmark_db):
    basecrud = CRUDBase(BookmarkModel, bookmark_db)
    instance = basecrud.safe_execute(operation="get_all")
    assert len(instance) >= 3


def test_custom_query(bookmark_db):
    basecrud = CRUDBase(BookmarkModel, bookmark_db)
    instance = basecrud.safe_execute(
        operation="custom_query", query="select * from bookmark"
    )
    assert len(instance) >= int(os.getenv("FAKE_DATA_NUM"))

    # test pagination
    instance = basecrud.safe_execute(
        operation="custom_query", query="select * from bookmark limit 2 offset 1"
    )
    assert len(instance) == 2
    assert instance[0]["id"] == 2
    assert instance[1]["id"] == 3

    instance = basecrud.safe_execute(
        operation="custom_query", query="select * from bookmark limit 2 offset 2"
    )
    assert len(instance) == 2
    assert instance[0]["id"] == 3
    assert instance[1]["id"] == 4

    instance = basecrud.safe_execute(
        operation="custom_query", query="select count(*) count from bookmark"
    )
    assert instance[0]["count"] >= int(os.getenv("FAKE_DATA_NUM"))
