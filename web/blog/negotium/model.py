from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean

from blog import Base


class NegotiumModel(Base):
    __tablename__ = "negotium"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime, nullable=False)
    priority = Column(Integer, nullable=False)
    completed = Column(Boolean, default=False)
    pid = Column(Integer, nullable=True, index=True)

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
        }
        if not test:
            json_data["timestamp"] = self.format_timestamp()

        return json_data


PRIORITY = {
    1: "Low",
    2: "Medium",
    3: "High",
    4: "Urgent",
}
