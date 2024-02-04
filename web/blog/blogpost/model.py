from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from blog import Base


class BlogPostModel(Base):
    __tablename__ = "blog_post"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    timestamp = Column(DateTime, default=datetime.utcnow)
    deleted = Column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<title {self.title}>"

    def format_timestamp(self, format="%Y-%m-%d %H:%M:%S"):
        return self.timestamp.strftime(format)

    def get_editable(self):
        return {
            "id": {"value": self.id, "disabled": True},
            "title": {"value": self.title, "disabled": True},
            "version": {"value": self.version, "disabled": True},
            "timestamp": {"value": self.timestamp, "disabled": True},
            "deleted": {"value": self.deleted, "disabled": False},
        }

    def to_json(self, test=False):
        json_data = {
            "title": self.title,
            "version": self.version,
        }
        if not test:
            json_data["id"] = self.id
            json_data["timestamp"] = self.format_timestamp()
            json_data["deleted"] = self.deleted
        return json_data
