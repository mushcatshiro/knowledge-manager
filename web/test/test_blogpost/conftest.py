import os

import pytest


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
