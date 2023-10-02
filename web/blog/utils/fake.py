import datetime
import random

from sqlalchemy.orm.attributes import InstrumentedAttribute


def create_fake_data(model, num=10):
    """
    Create fake data for testing
    Args:
    -----
    model: Model
        SQLAlchemy model class
    num: int
        number of fake data to be created
    Returns:
    --------
    instances: List[dict]
    """

    class Counter:
        def __init__(self, count):
            self.count = count
            self.container = {}

        def get_unique(self, attr, t):
            if attr not in self.container:
                self.container[attr] = []

            val = self.rand(t, max_int=128, max_str=16, str_chars="abcdefghijk")
            while val in self.container[attr]:
                val = self.rand(t, max_int=128, max_str=16, str_chars="abcdefghijk")
            self.container[attr].append(val)
            return val

        def get(self, attr, t):
            return self.rand(t)

        def rand(self, t, max_int=64, max_str=12, str_chars="abcdefghijk"):
            if t == int:
                return random.randint(1, 64)
            elif t == str:
                return "".join(random.choices(str_chars, k=max_str))

    counter = Counter(count=num)

    instances = []
    for _ in range(num):
        instance = model()
        for attr in dir(model):
            if (
                not attr.startswith("_")
                and isinstance(getattr(model, attr), InstrumentedAttribute)
                and attr != model.__table__.primary_key.columns[0].name
                and (
                    not model.__table__.columns[attr].nullable
                    or model.__table__.columns[attr].default is not None
                )
            ):
                if model.__table__.columns[attr].unique:
                    setattr(
                        instance,
                        attr,
                        counter.get_unique(
                            attr, model.__table__.columns[attr].type.python_type
                        ),
                    )
                else:
                    setattr(
                        instance,
                        attr,
                        counter.get(
                            attr, model.__table__.columns[attr].type.python_type
                        ),
                    )
        instance = instance.to_json(test=True)
        instances.append(instance)
    return instances
