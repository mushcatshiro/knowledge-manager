from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from blog import Base


class NegotiumModel(Base):
    __tablename__ = "negotium"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
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
