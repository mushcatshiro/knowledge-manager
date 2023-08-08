from sqlalchemy.orm import Session

from blog.core.crud import CRUDBase
from blog.models import BookmarkModel


def test_create(db):
    with Session(db) as session:
        obj = BookmarkModel(
            **{
                "title": "test",
                "url": "http://test.com",
                "img": "http://test.com/img",
                "desc": "test"}
        )
        session.add(obj)
        session.commit()
        assert obj.id == 1
        # query the inserted object
        obj = session.query(BookmarkModel).filter_by(id=1).first()
        assert obj.id == 1

def test_update(db):
    with Session(db) as session:
        # query entry from bookmark table with id = 1
        obj = session.query(BookmarkModel).filter_by(id=1).first()
        # update the entry
        obj.title = "test_update"
        session.commit()
        # query the updated entry
        obj = session.query(BookmarkModel).filter_by(id=1).first()
        assert obj.title == "test_update"
