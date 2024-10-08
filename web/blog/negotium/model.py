from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean

from blog import Base


class NegotiumModel(Base):
    __tablename__ = "negotium"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)  # TODO deprecated, to update
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
            if self.deadline is None or self.deadline < datetime.utcnow()
            else True,
            "completed": self.completed,
            "priority": PRIORITY.get(self.priority, "Low"),
        }
        if not test:
            json_data["timestamp"] = self.format_timestamp()

        return json_data


PRIORITY = {
    3: "Low",
    2: "Medium",
    1: "High",
    0: "Urgent",
}
