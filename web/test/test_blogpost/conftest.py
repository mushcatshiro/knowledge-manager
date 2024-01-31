import os

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import insert, delete


@pytest.fixture
def blogpost_db(db):
    """
    BUG
    ```
    fake_data = [
        {"title": "test title 1"},
        {"title": "test title -1", "version": 1},
        {"title": "test title -1", "version": 2, "deleted": 1},
    ]
    with Session(db) as session:
        session.execute(
            insert(BlogPostModel),
            fake_data,
        )
    ```
    does not work for some reason
    """
    from blog.blogpost import BlogPostModel

    instance_1 = BlogPostModel(title="test title 1")
    instance_2 = BlogPostModel(title="test title -1", version=1, deleted=1)
    instance_3 = BlogPostModel(title="test title -1", version=2, deleted=1)
    instance_4 = BlogPostModel(title="test title 0")
    instance_5 = BlogPostModel(title="test title 0", version=2)

    with Session(db) as session:
        session.add_all([instance_1, instance_2, instance_3, instance_4, instance_5])
        session.commit()
    yield db

    with Session(db) as session:
        session.execute(delete(BlogPostModel))
        session.commit()
