from blog import CustomException
from blog.core.crud import CRUDBase


def paginate(page: int, basecrud: CRUDBase, pagination_limit: int):
    """
    Paginate a query result
    Args:
        page (int): page number
        basecrud (CRUDBase): basecrud instance
        pagination_limit (int): pagination limit
    Returns:
        dict: paginated results
    Usage:
        ...
        p = paginate(
            page=1,
            query_string="select * from bookmark order by timestamp desc limit 10 offset 0",
            total_length_query_string="select count(*) as count from bookmark",
            basecrud=CRUDBase(BookmarkModel, db),
            pagination_limit=10
        )
        return render_template("bookmarklet.html", **p)
    """
    rv = basecrud.safe_execute(
        "paginate", limit=pagination_limit, offset=(page - 1) * pagination_limit
    )
    total_length = rv["total"]
    instances = rv["instances"]
    if not instances:
        raise CustomException(400, "No entry found", f"No entry found for page {page}")
    return {
        "instances": rv["instances"],
        "total": total_length,
        "has_prev": page > 1,
        "has_next": total_length > page * pagination_limit,
        "prev_num": page - 1 if page > 1 else None,
        "next_num": page + 1 if total_length > page * pagination_limit else None,
    }
