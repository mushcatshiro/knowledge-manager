from datetime import datetime, timedelta
import copy
from typing import Tuple, Optional, Dict
from enum import IntEnum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from blog.core.crud import Base


class State(IntEnum):
    New = 0
    Learning = 1
    Review = 2
    Relearning = 3


class Rating(IntEnum):
    Again = 1
    Hard = 2
    Good = 3
    Easy = 4

    @classmethod
    def convert(cls, rating: str) -> "Rating":
        if rating in cls.__members__:
            return cls.__members__[rating]
        raise ValueError


class ReviewLogModel(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "review_logs"
    rid = Column(Integer, primary_key=True, index=True)
    rating: int = Column(Integer)
    elapsed_days: int = Column(Integer)
    scheduled_days: int = Column(Integer)
    review: datetime = Column(DateTime)
    state: int = Column(Integer)
    id = Column(Integer, ForeignKey("cards.id"))
    card = relationship("CardModel", back_populates="review_logs")


class ReviewLog:
    rating: int
    elapsed_days: int
    scheduled_days: int
    Review: datetime
    state: int

    def __init__(
        self,
        rating: int,
        elapsed_days: int,
        scheduled_days: int,
        review: datetime,
        state: int,
    ):
        self.rating = rating
        self.elapsed_days = elapsed_days
        self.scheduled_days = scheduled_days
        self.review = review
        self.state = state


class CardModel(Base):  # pylint: disable=too-few-public-methods
    """
    Card model
    TODO
    ----
    - chinese support
    - image support
    - audio support
    - video support
    - latex support
    - markdown support
    """

    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, index=True)
    due: datetime = Column(DateTime, default=datetime.utcnow)
    stability: float = Column(Integer, default=0)
    difficulty: float = Column(Integer, default=0)
    elapsed_days: int = Column(Integer, default=0)
    scheduled_days: int = Column(Integer, default=0)
    reps: int = Column(Integer, default=0)
    lapses: int = Column(Integer, default=0)
    state: State = Column(Integer, default=State.New)
    last_review: datetime = Column(DateTime, nullable=True)
    title = Column(String, index=True)
    question = Column(String)
    answer = Column(String)
    review_logs = relationship("ReviewLogModel", back_populates="card")

    def __repr__(self) -> str:
        return f"<id {self.id} title {self.title}>"

    def get_fsrs_details(self):
        return {
            "due": self.due,
            "stability": self.stability,
            "difficulty": self.difficulty,
            "elapsed_days": self.elapsed_days,
            "scheduled_days": self.scheduled_days,
            "reps": self.reps,
            "lapses": self.lapses,
            "state": self.state,
            "last_review": self.last_review,
        }

    def update_fsrs_details(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def render(self) -> str:
        raise NotImplementedError

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "due": self.due,
            "stability": self.stability,
            "difficulty": self.difficulty,
            "elapsed_days": self.elapsed_days,
            "scheduled_days": self.scheduled_days,
            "reps": self.reps,
            "lapses": self.lapses,
            "state": self.state,
            "last_review": self.last_review,
            "title": self.title,
            "question": self.question,
            "answer": self.answer,
        }


class Card:
    due: datetime
    stability: float
    difficulty: float
    elapsed_days: int
    scheduled_days: int
    reps: int
    lapses: int
    state: State
    last_review: datetime

    def __init__(
        self,
        due=None,
        stability=0,
        difficulty=0,
        elapsed_days=0,
        scheduled_days=0,
        reps=0,
        lapses=0,
        state=None,
        last_review=None,
    ) -> None:
        """
        TODO
        ----
        self.last_review should be set to None if state is New and maybe also
        when state is relearning.
        """
        self.due = due if due else datetime.utcnow()
        self.stability = stability
        self.difficulty = difficulty
        self.elapsed_days = elapsed_days
        self.scheduled_days = scheduled_days
        self.reps = reps
        self.lapses = lapses
        self.state = state if state else State.New
        self.last_review = last_review if last_review else datetime.utcnow()

    def get_retrievability(self, now: datetime) -> Optional[float]:
        if self.state == State.Review:
            elapsed_days = max(0, (now - self.last_review).days)
            return (1 + elapsed_days / (9 * self.stability)) ** -1
        return None


class SchedulingInfo:
    card: Card
    Review_log: ReviewLog

    def __init__(self, card: Card, review_log: ReviewLog) -> None:
        self.card = card
        self.review_log = review_log


class SchedulingCards:
    again: Card
    hard: Card
    good: Card
    easy: Card

    def __init__(self, card: Card) -> None:
        self.again = copy.deepcopy(card)
        self.hard = copy.deepcopy(card)
        self.good = copy.deepcopy(card)
        self.easy = copy.deepcopy(card)

    def update_state(self, state: State):
        if state == State.New:
            self.again.state = State.Learning
            self.hard.state = State.Learning
            self.good.state = State.Learning
            self.easy.state = State.Review
            self.again.lapses += 1
        elif state in (State.Learning, State.Relearning):
            self.again.state = state
            self.hard.state = state
            self.good.state = State.Review
            self.easy.state = State.Review
        elif state == State.Review:
            self.again.state = State.Relearning
            self.hard.state = State.Review
            self.good.state = State.Review
            self.easy.state = State.Review
            self.again.lapses += 1

    def schedule(
        self,
        now: datetime,
        hard_interval: float,
        good_interval: float,
        easy_interval: float,
    ):
        self.again.scheduled_days = 0
        self.hard.scheduled_days = hard_interval
        self.good.scheduled_days = good_interval
        self.easy.scheduled_days = easy_interval
        self.again.due = now + timedelta(minutes=5)
        if hard_interval > 0:
            self.hard.due = now + timedelta(days=hard_interval)
        else:
            self.hard.due = now + timedelta(minutes=10)
        self.good.due = now + timedelta(days=good_interval)
        self.easy.due = now + timedelta(days=easy_interval)

    def record_log(self, card: Card, now: datetime) -> Dict[int, SchedulingInfo]:
        return {
            Rating.Again: SchedulingInfo(
                self.again,
                ReviewLog(
                    Rating.Again,
                    self.again.scheduled_days,
                    card.elapsed_days,
                    now,
                    card.state,
                ),
            ),
            Rating.Hard: SchedulingInfo(
                self.hard,
                ReviewLog(
                    Rating.Hard,
                    self.hard.scheduled_days,
                    card.elapsed_days,
                    now,
                    card.state,
                ),
            ),
            Rating.Good: SchedulingInfo(
                self.good,
                ReviewLog(
                    Rating.Good,
                    self.good.scheduled_days,
                    card.elapsed_days,
                    now,
                    card.state,
                ),
            ),
            Rating.Easy: SchedulingInfo(
                self.easy,
                ReviewLog(
                    Rating.Easy,
                    self.easy.scheduled_days,
                    card.elapsed_days,
                    now,
                    card.state,
                ),
            ),
        }


class Parameters:
    request_retention: float
    maximum_interval: int
    w: Tuple[float, ...]

    def __init__(self) -> None:
        self.request_retention = 0.9
        self.maximum_interval = 36500
        self.w = (
            0.4,
            0.6,
            2.4,
            5.8,
            4.93,
            0.94,
            0.86,
            0.01,
            1.49,
            0.14,
            0.94,
            2.18,
            0.05,
            0.34,
            1.26,
            0.29,
            2.61,
        )
