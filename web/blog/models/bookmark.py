from datetime import datetime

from blog import db, ma


class BookmarkModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    url = db.Column(db.String, unique=True, nullable=False)
    img = db.Column(db.String, nullable=False)
    desc = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return "<title %r>" % self.title


class BookmarkSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BookmarkModel


class Bookmark:
    def __init__(self) -> None:
        # self.serializer = BookmarkSchema(many=True)
        pass

    def create(self, payload):
        bookmark = BookmarkModel(**payload)
        db.session.add(bookmark)
        db.session.commit()
        return BookmarkSchema().dump(bookmark)

    def read(self):
        result = db.session.execute(db.select(BookmarkModel)).scalars().all()
        # TODO validate many
        return BookmarkSchema(many=True).dump(result)
            

    def update(self):
        pass

    def delete(self):
        pass