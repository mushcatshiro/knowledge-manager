from blog.core.crud import CRUDBase
from sqlalchemy import select, func
from datetime import datetime, timezone
from blog.negotium.model import PRIORITY


class NegotiumCRUD(CRUDBase):
    def __init__(self, model, engine):
        super().__init__(model, engine)

    def get_negotium_chain(self, negotium_id: int):
        """
        Get all negotiums in a chain top down from the given negotium id
        """
        stmt = (
            "WITH RECURSIVE cte (id, title, content, timestamp, deadline, priority, completed, pid) AS ( "
            "SELECT id, title, content, timestamp, deadline, priority, completed, pid FROM negotium "
            f"WHERE id = {negotium_id} "
            "UNION ALL "
            "SELECT n.id, n.title, n.content, n.timestamp, n.deadline, n.priority, n.completed, n.pid FROM cte "
            "INNER JOIN negotium n ON cte.id = n.pid "
            ") "
            "SELECT * FROM cte"
        )

        instances = self.safe_execute(
            "custom_query",
            query=stmt,
        )
        resp = []
        for instance in instances:
            tmp = {}
            tmp["id"] = instance["id"]
            tmp["title"] = instance["title"]
            tmp["content"] = instance["content"]
            tmp["timestamp"] = instance["timestamp"]
            tmp["pid"] = instance["pid"]
            tmp["completed"] = True if instance["completed"] == 1 else False
            tmp["is_overdue"] = (
                False
                if instance["deadline"] is None
                or not datetime.strptime(instance["deadline"], "%Y-%m-%d %H:%M:%S.%f")
                < datetime.now(timezone.utc)
                else True
            )
            tmp["priority"] = PRIORITY.get(instance["priority"], "Low")
            resp.append(tmp)
        return resp

    def get_all_root_negotiums(self, session, query, **kwargs):
        """
        Get all root negotiums
        """
        del kwargs, query
        instances = (
            session.execute(select(self.model).where(self.model.pid.is_(None)))
            .scalars()
            .all()
        )
        return [instance.to_json() for instance in instances]

    def get_priority_matrix(self, session, query, **kwargs):
        """
        Get the priority matrix
        """
        del kwargs, query
        instances = session.execute(
            select(self.model.priority, func.count().label("cnt")).group_by(
                self.model.priority
            )
        ).all()
        return [{"priority": instance[0], "cnt": instance[1]} for instance in instances]


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
