from blog.core.crud import CRUDBase


class NegotiumCRUD(CRUDBase):
    def __init__(self, model, engine):
        super().__init__(model, engine)

    def get_negotium_chain(self, negotium_id: int):
        """
        Get all negotiums in a chain top down from the given negotium id
        """
        stmt = (
            "WITH RECURSIVE cte (id, title, content, timestamp, pid) AS ( "
            "SELECT id, title, content, timestamp, pid FROM negotium "
            f"WHERE id = {negotium_id} "
            "UNION ALL "
            "SELECT n.id, n.title, n.content, n.timestamp, n.pid FROM cte "
            "INNER JOIN negotium n ON cte.id = n.pid "
            ") "
            "SELECT * FROM cte"
        )

        instances = self.execute(
            "custom_query",
            query=stmt,
        )
        return instances


def negotium_tree_search(id_pairs, target_id):
    """
    Search the tree for the given target_id

    args
    ----
    id_pairs: list
        list of dicts with keys "id" and "pid"
    target_id: int

    returns
    -------
    count: int
        total number of childs of target_id in the tree
    """
    count = 0
    for id_pair in id_pairs:
        if id_pair["pid"] == target_id:
            count += 1
            count += negotium_tree_search(id_pairs, id_pair["id"])
    return count
