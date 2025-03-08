import pytest

from blog.negotium import NegotiumCRUD, NegotiumModel, negotium_tree_search


@pytest.mark.timeout(30)
def test_query_negotium_chain(negotium_db):
    """
    Test the query for the negotium chain

    TODO
    ----
    - remove hardcoded values
    """
    chain_test = [
        [1, None],
        [2, 1],
        [3, 1],
        [4, 1],
        [5, 2],
        [6, 2],
        [7, 3],
        [8, 3],
        [9, 4],
        [10, 4],
    ]
    engine, _ = negotium_db
    basecrud = NegotiumCRUD(NegotiumModel, engine)
    for i, j in chain_test:
        basecrud.safe_execute("update", id=i, pid=j)
    id_pairs = basecrud.safe_execute(
        operation="custom_query",
        query="select id, pid from negotium order by id asc",
    )
    instances = basecrud.get_negotium_chain(negotium_id=1)
    assert len(instances) == negotium_tree_search(id_pairs, 1) + 1


def test_get_priority_matrix(negotium_db):
    """
    priority matrix always returns all 4 priority levels
    """
    engine, total = negotium_db
    basecrud = NegotiumCRUD(NegotiumModel, engine)
    priority_matrix = basecrud.safe_execute("get_priority_matrix")
    assert len(priority_matrix) == 4


def test_get_all_root_negotiums(negotium_db):
    """
    Test the query for the root negotiums

    TODO
    ----
    - remove hardcoded values
    """
    engine, total = negotium_db
    basecrud = NegotiumCRUD(NegotiumModel, engine)
    basecrud.safe_execute("update", id=1, pid=None)
    root_negotiums = basecrud.safe_execute("get_all_root_negotiums")
    assert len(root_negotiums) == 1


def test_get_root_negotiums_by_priority(negotium_db):
    """
    Test the query for the root negotiums
    """
    engine, total = negotium_db
    basecrud = NegotiumCRUD(NegotiumModel, engine)
    for i in range(total):
        basecrud.safe_execute("update", id=i + 1, pid=None, priority=3)
    basecrud.safe_execute("update", id=1, pid=None, priority=1, completed=False)
    basecrud.safe_execute("update", id=2, pid=None, priority=1, completed=True)
    basecrud.safe_execute("update", id=3, pid=None, priority=1, completed=True)
    root_negotiums = basecrud.safe_execute(
        "get_root_negotiums_by_priority", priority=1, mode="all"
    )
    assert len(root_negotiums) == 3
    root_negotiums = basecrud.safe_execute(
        "get_root_negotiums_by_priority", priority=1, mode="pending"
    )
    assert len(root_negotiums) == 1
