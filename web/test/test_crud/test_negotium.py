from blog.negotium import NegotiumCRUD, NegotiumModel, negotium_tree_search


def test_query_negotium_chain(db):
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
    basecrud = NegotiumCRUD(NegotiumModel, db)
    for i, j in chain_test:
        basecrud.execute("update", id=i, pid=j)
    id_pairs = basecrud.execute(
        operation="custom_query",
        query="select id, pid from negotium order by id asc",
    )
    instances = basecrud.get_negotium_chain(negotium_id=1)
    assert len(instances) == negotium_tree_search(id_pairs, 1) + 1
