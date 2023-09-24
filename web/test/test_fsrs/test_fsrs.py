import datetime as dt

from blog.fsrs import FSRS, Rating, Card

from blog.core.crud import CRUDBase
from blog.fsrs.model import CardModel


def print_scheduling_cards(scheduling_cards):
    print()
    print("again.card:", scheduling_cards[Rating.Again].card.__dict__)
    print("again.review_log:", scheduling_cards[Rating.Again].review_log.__dict__)
    print("hard.card:", scheduling_cards[Rating.Hard].card.__dict__)
    print("hard.review_log:", scheduling_cards[Rating.Hard].review_log.__dict__)
    print("good.card:", scheduling_cards[Rating.Good].card.__dict__)
    print("good.review_log:", scheduling_cards[Rating.Good].review_log.__dict__)
    print("easy.card:", scheduling_cards[Rating.Easy].card.__dict__)
    print("easy.review_log:", scheduling_cards[Rating.Easy].review_log.__dict__)
    print()


def test_repeat():
    f = FSRS()
    f.p.w = (
        1.14,
        1.01,
        5.44,
        14.67,
        5.3024,
        1.5662,
        1.2503,
        0.0028,
        1.5489,
        0.1763,
        0.9953,
        2.7473,
        0.0179,
        0.3105,
        0.3976,
        0.0,
        2.0902,
    )
    card = Card()
    now = dt.datetime(2022, 11, 29, 12, 30, 0, 0)
    scheduling_cards = f.repeat(card, now)
    print_scheduling_cards(scheduling_cards)

    ratings = (
        Rating.Good,
        Rating.Good,
        Rating.Good,
        Rating.Good,
        Rating.Good,
        Rating.Good,
        Rating.Again,
        Rating.Again,
        Rating.Good,
        Rating.Good,
        Rating.Good,
        Rating.Good,
        Rating.Good,
    )
    ivl_history = []

    for rating in ratings:
        card = scheduling_cards[rating].card
        ivl = card.scheduled_days
        ivl_history.append(ivl)
        now = card.due
        scheduling_cards = f.repeat(card, now)
        print_scheduling_cards(scheduling_cards)

    print(ivl_history)
    assert ivl_history == [0, 5, 16, 43, 106, 236, 0, 0, 12, 25, 47, 85, 147]


def test_functionality(db):
    instance, engine = db
    cb = CRUDBase(CardModel, engine)
    instance = cb.execute(operation="get", id=1)
    c_details = instance.get_fsrs_details()
    f = FSRS()
    card = Card(**c_details)
    now = dt.datetime(2023, 9, 3, 22, 0, 0, 0)
    scheduling_cards = f.repeat(card, now)
    c = scheduling_cards[Rating.convert("Easy")].card.__dict__
    instance.update_fsrs_details(**c)
    cb = CRUDBase(CardModel, engine)
    instance = cb.execute("update", **instance.to_dict())
