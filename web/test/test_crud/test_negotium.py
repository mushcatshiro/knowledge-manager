from blog.negotium import NegotiumCRUD, NegotiumModel, negotium_tree_search


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


def test_query_negotium_chain_2(negotium_db):
    engine, _ = negotium_db
    basecrud = NegotiumCRUD(NegotiumModel, engine)
    instances = basecrud.get_negotium_chain(negotium_id=1)
    assert type(instances) == list
    assert type(instances[0]) == dict


def test_get_priority_matrix(negotium_db):
    """
    Test the query for the priority matrix

    TODO
    ----
    - remove hardcoded values
    """
    engine, total = negotium_db
    basecrud = NegotiumCRUD(NegotiumModel, engine)
    priority_matrix = basecrud.safe_execute("get_priority_matrix")
    assert len(priority_matrix) <= 3


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
