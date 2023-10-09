import random

from sqlalchemy.orm.attributes import InstrumentedAttribute


def create_fake_data(model, num=10, max_int=64, max_str=12, str_chars="abcdefghijk"):
    """
    Create fake data for testing
    Args:
    -----
    model: Model
        SQLAlchemy model class
    num: int
        number of fake data to be created
    max_int: int
        maximum integer value
    max_str: int
        maximum string length
    str_chars: str
        characters to be used for creating fake string
    Returns:
    --------
    instances: List[dict]
    """

    class Counter:
        def __init__(self, count, max_int, max_str, str_chars):
            self.count = count
            self.container = {}
            self.max_int = max_int
            self.max_str = max_str
            self.str_chars = str_chars

        def get_unique(self, attr, t):
            if attr not in self.container:
                self.container[attr] = []

            val = self.rand(t)
            while val in self.container[attr]:
                val = self.rand(t)
            self.container[attr].append(val)
            return val

        def get(self, attr, t):
            return self.rand(t)

        def rand(self, t):
            if t == int:
                return random.randint(1, self.max_int)
            elif t == str:
                return "".join(random.choices(self.str_chars, k=self.max_str))

    counter = Counter(count=num, max_int=max_int, max_str=max_str, str_chars=str_chars)

    instances = []
    for _ in range(num):
        instance = model()
        for attr in dir(model):
            if (
                not attr.startswith("_")
                and isinstance(getattr(model, attr), InstrumentedAttribute)
                and attr != model.__table__.primary_key.columns[0].name
                and (
                    (
                        not model.__table__.columns[attr].nullable
                        or model.__table__.columns[attr].default is not None
                    )
                    or (
                        model.__table__.columns[attr].default is None
                        and model.__table__.columns[attr].nullable
                    )
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
