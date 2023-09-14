from blog.core.crud import CRUDBase
from blog.bookmark import BookmarkModel


def test_create(db):
    basecrud = CRUDBase(BookmarkModel, db)
    instance = basecrud.execute(
        operation="create",
        title="test4",
        url="http://test4.com",
        img="http://test4.com/img",
        desc="test4",
    )
    assert instance.id == 4
    # query the inserted object
    instance = basecrud.execute(operation="get", id=4)
    assert instance.id == 4


def test_update(db):
    basecrud = CRUDBase(BookmarkModel, db)
    # update the entry with id = 1
    instance = basecrud.execute(
        operation="update",
        id=1,
        title="test_update",
        url="http://test_update.com",
        img="http://test_update.com/img",
        desc="test_update",
    )
    assert instance.id == 1
    # query the updated entry
    instance = basecrud.execute(operation="get", id=1)
    assert instance.id == 1
    assert instance.title == "test_update"
    assert instance.url == "http://test_update.com"
    assert instance.img == "http://test_update.com/img"
    assert instance.desc == "test_update"


def test_get_all(db):
    basecrud = CRUDBase(BookmarkModel, db)
    instance = basecrud.execute(operation="get_all",)
    print(instance)
    assert len(instance.to_json()) == 3
    # query the inserted object