from sqlalchemy.orm import Session
from sqlalchemy import text, select
from sqlalchemy.orm import declarative_base

import logging


logger = logging.getLogger(__name__)


Base = declarative_base()


class CRUDBase:
    def __init__(self, model, engine):
        self.model = model
        self.engine = engine

    def get(self, session, model, query, **kwargs):
        """
        Get an instance of a model with the given id
        Args:
        -----
        session: Session
            SQLAlchemy session object bound to the engine
        model: Model
            SQLAlchemy model class
        id: int
            id of the instance to be fetched
        Returns:
        --------
        instance: Model
        """
        del query
        instance = (
            session.execute(select(model).where(model.id == kwargs.get("id")))
            .scalars()
            .first()
        )
        return instance

    def get_all(self, session, model, query, **kwargs):
        """
        Get an instance of a model with the given id
        Args:
        -----
        session: Session
            SQLAlchemy session object bound to the engine
        model: Model
            SQLAlchemy model class
        id: int
            id of the instance to be fetched
        Returns:
        --------
        instance: Model
        """
        del query
        instance = session.execute(select(model))
        return instance

    def create(self, session, model, query, **kwargs):
        """
        Create an instance of a model with the given kwargs
        Args:
        -----
        session: Session
            SQLAlchemy session object bound to the engine
        model: Model
            SQLAlchemy model class
        **kwargs:
            key-value pairs of the columns to be created
        Returns:
        --------
        instance: Model
        """
        del query
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

    def _bulk_insert(self, session, model, query, **kwargs):
        """
        temporary unexposed method for testing
        """
        pass

    def update(self, session, model, query, **kwargs):
        """
        Update an instance of a model with the given id one entry at a time
        Args:
        -----
        session: Session
            SQLAlchemy session object bound to the engine
        model: Model
            SQLAlchemy model class
        **kwargs:
            key-value pairs of the columns to be updated, id is required
        Returns:
        --------
        instance: Model

        TODO
        ----
        - should not include id during updating
        """
        del query
        instance = self.get(session, model, query=None, id=kwargs.get("id"))
        if not instance:
            raise Exception(f"instance with {id} not found")
        for key, value in kwargs.items():
            setattr(instance, key, value)
        session.commit()
        return instance

    def delete(self, session, model, query, **kwargs):
        """
        Delete an instance of a model with the given id
        Args:
        -----
        session: Session
            SQLAlchemy session object bound to the engine
        model: Model
            SQLAlchemy model class
        **kwargs:
            key-value pairs of the columns to be updated, id is required
        Returns:
        --------
        instance: Model
        """
        del query
        instance = self.get(session, model, kwargs.get("id"))
        if not instance:
            raise Exception(f"instance with {id} not found")
        session.delete(instance)
        session.commit()
        return instance

    def custom_query(self, session: Session, model, query: str, **kwargs):
        """
        Execute a custom raw sql query
        """
        del model
        del kwargs
        instance = session.execute(text(query))
        return instance

    def execute(self, operation, query=None, **kwargs):
        if not hasattr(self, operation):
            raise Exception(f"operation {operation} not found")
        fn = getattr(self, operation)
        with Session(self.engine) as session:
            try:
                resp = fn(session, self.model, query, **kwargs)
            except Exception as e:
                session.rollback()
                logger.error(e)
                return None
            else:
                # refresh the instance to get the latest data
                # or make sure BookmarksModel is bound to some session
                session.refresh(resp)
                return resp
