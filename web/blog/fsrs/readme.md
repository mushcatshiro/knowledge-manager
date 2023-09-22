# fsrs

this is a copy of [py-fsrs][1] which is an implementation of fsrsv4. it has some
[flaws][2] described in the reddit posts. the documentation is still not ready
at the moment and to minimize friction to fsrs adoption to km, it will be
utilized such described below.

```python
cb = CRUDBase(CardModel, db)
instance = cb.execute("get", id=1)
# get some user review of card {"rating": "good", "cid": 1}
c_details = instance.get_fsrs_details()
f = FSRS()
c = Card(**c_details)
now = datetime(2023, 9, 3, 22, 0, 0, 0)
scheduling_cards = f.repeat(card, now)
c = scheduling_cards[Rating.Good].card.__dict__
instance.update_fsrs_details(**c)
cb = CRUDBase(CardModel, db)
instance = cb.execute("update", **instance.to_dict())
```


[1]: https://github.com/open-spaced-repetition/py-fsrs
[2]: https://www.reddit.com/r/Anki/comments/15mab3r/fsrs_explained_part_1_what_it_is_and_how_it_works/
