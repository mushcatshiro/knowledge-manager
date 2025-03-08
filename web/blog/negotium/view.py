import datetime as dt

from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    current_app,
)
from sqlalchemy import create_engine
from blog import CustomException
from blog.auth import protected
from blog.negotium import NegotiumCRUD, NegotiumModel, REVERSED_PRIORITY
import logging

logger = logging.getLogger(__name__)

negotium_blueprint = Blueprint("negotium", __name__)


@negotium_blueprint.route("/", methods=["GET"])
@protected
def index():
    # TODO efficient search
    priority = request.args.get("priority", default=0, type=int)
    db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    priority_matrix = NegotiumCRUD(NegotiumModel, db).safe_execute(
        "get_priority_matrix"
    )
    root_negotiums = NegotiumCRUD(NegotiumModel, db).safe_execute(
        "get_root_negotiums_by_priority", priority=priority, mode="pending"
    )
    db.dispose()

    return render_template(
        "negotiums.html",
        logged_in=True,
        priority_matrix=priority_matrix,
        root_negotiums=root_negotiums,
        priority=REVERSED_PRIORITY[priority],
    )


@negotium_blueprint.route("/chain/<int:nid>", methods=["GET"])
@protected
def chain_by_nid(nid):
    # TODO provides a chain of negotiums from the given nid
    # TODO consider also provide parents
    db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    negotiums = NegotiumCRUD(NegotiumModel, db).get_negotium_chain(nid)
    logger.debug(f"negotiums: {negotiums}")
    return render_template(
        "negchain.html",
        logged_in=True,
        negotiums=negotiums,
    )


@negotium_blueprint.route("/chain2/<int:nid>", methods=["GET"])
@protected
def chain_by_nid_v2(nid):
    # TODO provides a chain of negotiums from the given nid
    # TODO consider also provide parents
    db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    negotiums = NegotiumCRUD(NegotiumModel, db).get_negotium_chain_v2(nid)
    logger.debug(f"negotiums: {negotiums}")
    return render_template(
        "negchain2.html",
        logged_in=True,
        tree_data=negotiums,
    )


@negotium_blueprint.route("/get/<int:nid>", methods=["GET"])
@protected
def negotium_by_nid(nid):
    # TODO consider merging to `model_edit.html`
    # TODO creates link to create a new negotium with pid and link to edit negotium
    db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    instance = NegotiumCRUD(NegotiumModel, db).safe_execute("get", id=nid)
    return render_template(
        "negentry.html",
        logged_in=True,
        form_type="View Negotium By ID",
        can_submit=False,
        pid=None,
        instance=instance,
    )


@negotium_blueprint.route("/edit/<int:nid>", methods=["GET", "POST"])
@protected
def edit_negotium(nid):
    db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    if request.method == "POST":
        fields = {
            "title": request.form.get("title"),
            "content": request.form.get("content"),
        }
        for key in [
            "deadline",
            "priority",
            "completed",
            "pid",
        ]:  # TODO consider adding to `NegotiumModel`
            value = request.form.get(key)
            if key == "deadline" and value:
                try:
                    value = dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    raise CustomException(400, "Invalid deadline format", "Bad request")
                else:
                    fields[key] = value
            elif key == "completed":
                logger.debug(f"value: {value}")
                fields[key] = True if value == "1" else False
            elif value:
                fields[key] = value
        logger.debug(f"fields: {fields}")
        instance = NegotiumCRUD(NegotiumModel, db).safe_execute(
            "update", id=nid, **fields
        )
        logger.debug(f"instance: {instance}")
        if instance is None:
            raise CustomException(400, "Negotium not updated", "Bad request")
        return redirect(url_for("negotium.index"))
    instance = NegotiumCRUD(NegotiumModel, db).safe_execute("get", id=nid)
    return render_template(
        "negentry.html",
        logged_in=True,
        form_type="Edit Negotium",
        can_submit=True,
        pid=None,
        instance=instance,
    )


@negotium_blueprint.route("/create/", methods=["GET", "POST"])
@negotium_blueprint.route("/create/<int:pid>", methods=["GET", "POST"])
@protected
def create_negotium(pid=None):
    """
    TODO handle updating root i.e. existing chain's root is now a child of new
    neg
    """
    if request.method == "POST":
        fields = {
            "title": request.form.get("title"),
            "content": request.form.get("content"),
        }
        for key in [
            "deadline",
            "priority",
            "completed",
            "pid",
        ]:  # TODO consider adding to `NegotiumModel`
            value = request.form.get(key)
            if key == "deadline" and value:
                try:
                    value = dt.datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    raise CustomException(400, "Invalid deadline format", "Bad request")
                else:
                    fields[key] = value
            elif key == "completed":
                fields[key] = True if value == 1 else False
            elif value:
                fields[key] = value
        db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
        instance = NegotiumCRUD(NegotiumModel, db).safe_execute("create", **fields)
        if instance is None:
            raise CustomException(400, "Negotium not created", "Bad request")
        return redirect(url_for("negotium.index"))
    # TODO consider adding to `NegotiumModel`
    instance = {
        "id": "",
        "title": "",
        "content": "",
        "timestamp": "",
        "deadline": "",
        "priority": "",
        "completed": False,
        "pid": "" if pid is None else pid,
    }
    return render_template(
        "negentry.html",
        logged_in=True,
        form_type="Create Negotium",
        can_submit=True,
        pid=pid,
        instance=instance,
    )
