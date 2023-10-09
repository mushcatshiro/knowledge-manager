from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from blog import Base


class BookmarkModel(Base):
    __tablename__ = "bookmark"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    img = Column(String, nullable=False)
    desc = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<title {self.title}>"

    def format_timestamp(self, format="%Y-%m-%d %H:%M:%S"):
        return self.timestamp.strftime(format)

    def get_editable(self):
        return {
            "id": {"value": self.id, "disabled": True},
            "title": {"value": self.title, "disabled": True},
            "url": {"value": self.url, "disabled": True},
            "img": {"value": self.img, "disabled": True},
            "desc": {"value": self.desc, "disabled": False},
            "timestamp": {"value": self.timestamp, "disabled": True},
        }

    def to_json(self, test=False):
        # handle multiple query results
        # not required as session.execute returns a list of BaseModels
        # if isinstance(self, list):
        #     return [item.to_json() for item in self]
        json_data = {
            "title": self.title,
            "url": self.url,
            "img": self.img,
            "desc": self.desc,
        }
        if not test:
            json_data["id"] = self.id
            json_data["timestamp"] = self.format_timestamp()
        return json_data
