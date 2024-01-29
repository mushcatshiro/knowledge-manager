import pytest


@pytest.fixture(scope="module")
def container_setup():
    # issue container build -> run cmd
    assert True
    yield
    # issue container teardown -> cleanup cmd
