import os

import pytest


@pytest.fixture(scope="session")
def auth_token(session_setup):
    _, test_app = session_setup
    client = test_app.test_client()
    response = client.post("/auth/authenticate", json={"auth": test_app.config["AUTH"]})
    return response.json["token"]


@pytest.fixture
def cleanup_file(session_setup):
    _, test_app = session_setup
    delete_files = []
    yield delete_files
    for file in delete_files:
        fpath = os.path.join(test_app.config["BLOG_PATH"], file)
        if os.path.exists(fpath):
            os.remove(fpath)
        else:
            print(f"The file {fpath} does not exist, something is wrong")
