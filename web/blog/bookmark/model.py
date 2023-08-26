from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from blog.core.crud import Base


class BookmarkModel(Base):
    __tablename__ = "bookmark"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    img = Column(String, nullable=False)
    desc = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return "<title %r>" % self.title

    def to_json(self):
        # handle multiple enquiry
        if isinstance(self, list):
            return [item.to_json() for item in self]
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "img": self.img,
            "desc": self.desc,
            "timestamp": self.timestamp,
        }
