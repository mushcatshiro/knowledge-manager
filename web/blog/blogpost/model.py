from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from blog import Base


class BlogPostModel(Base):
    __tablename__ = "blog_post"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    timestamp = Column(DateTime(timezone=True), default=func.now())  # datetime.utcnow
    deleted = Column(Integer, default=0)
    private = Column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<title {self.title}>"

    def format_timestamp(self, format="%Y-%m-%d %H:%M:%S"):
        return self.timestamp.strftime(format)

    def get_editable(self):
        return {
            "id": {"value": self.id, "readonly": True},
            "title": {"value": self.title},
            "version": {"value": self.version, "readonly": True},
            "timestamp": {"value": self.timestamp},
            "deleted": {"value": self.deleted},
            "private": {"value": self.private, "checkbox": True},
        }

    def to_json(self, test=False) -> dict:
        json_data = {
            "title": self.title,
            "version": self.version,
            "timestamp": self.format_timestamp(),
            "private": self.private,
        }
        if not test:
            json_data["id"] = self.id
            json_data["timestamp"] = self.format_timestamp()
            json_data["deleted"] = self.deleted
        return json_data
