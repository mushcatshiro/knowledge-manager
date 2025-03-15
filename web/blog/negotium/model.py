from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from blog import Base


class NegotiumModel(Base):
    __tablename__ = "negotium"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=func.now())
    deadline = Column(DateTime, nullable=True)
    priority = Column(Integer, nullable=True)
    completed = Column(Boolean, default=False)
    pid = Column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<title {self.title}>"

    def format_timestamp(self, format="%Y-%m-%d %H:%M:%S"):
        return self.timestamp.strftime(format)

    def to_json(self, test=False):
        json_data = {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp,
            "pid": self.pid,
            "is_overdue": False
            if self.deadline is None or self.deadline < datetime.now()
            else True,
            "completed": self.completed,
            "priority": PRIORITY.get(self.priority, "Low"),
        }
        if not test:
            json_data["timestamp"] = self.format_timestamp()
        else:
            del json_data["is_overdue"], json_data["id"]
            json_data["priority"] = REVERSED_PRIORITY.get(self.priority, 3)

        return json_data

    @staticmethod
    def get_empty_instance(pid=None):
        return {
            "id": "",
            "title": "",
            "content": "",
            "timestamp": "",
            "deadline": "",
            "priority": "",
            "completed": False,
            "pid": "" if pid is None else pid,
        }


class NegBlogLinkerModel:
    # TODO to inherit from Base
    __tablename__ = "negotium_blog_linker"
    blog_id = Column(Integer, nullable=False)
    negotium_id = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<NegBlogLinker {self.id}>"


PRIORITY = {
    0: "Urgent",
    1: "High",
    2: "Medium",
    3: "Low",
}

REVERSED_PRIORITY = {v: k for k, v in PRIORITY.items()}
