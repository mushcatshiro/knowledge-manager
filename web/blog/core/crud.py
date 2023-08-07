class CRUDBase:
    def __init__(self):
        self.model = None

    def get(self, id):
        return self.model.query.get(id)

    def get_all(self):
        return self.model.query.all()

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, id, **kwargs):
        instance = self.get(id)
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.session.commit()
        return instance

    def delete(self, id):
        instance = self.get(id)
        db.session.delete(instance)
        db.session.commit()
        return instance