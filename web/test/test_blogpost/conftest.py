import os

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import delete


@pytest.fixture
def blogpost_db(session_setup):
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
    engine, _ = session_setup
    from blog.blogpost import BlogPostModel

    instance_1 = BlogPostModel(title="test title 1")
    instance_2 = BlogPostModel(title="test title -1", version=1, deleted=1)
    instance_3 = BlogPostModel(title="test title -1", version=2, deleted=1)
    instance_4 = BlogPostModel(title="test title 0")
    instance_5 = BlogPostModel(title="test title 0", version=2)

    with Session(engine) as session:
        session.add_all([instance_1, instance_2, instance_3, instance_4, instance_5])
        session.commit()
    yield engine

    with Session(engine) as session:
        session.execute(delete(BlogPostModel))
        session.commit()


@pytest.fixture
def cleanup_blog(session_setup):
    _, test_app = session_setup
    delete_list = []
    yield delete_list
    for i in delete_list:
        try:
            os.remove(os.path.join(test_app.config["BLOG_PATH"], i))
        except Exception as e:
            print(e)
