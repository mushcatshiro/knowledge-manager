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
from blog.negotium import NegotiumCRUD, NegotiumModel, NegBlogLinkerModel, PRIORITY
import logging

logger = logging.getLogger(__name__)

negotium_blueprint = Blueprint("negotium", __name__)


@negotium_blueprint.route("/", methods=["GET"])
@protected
def index():
    # TODO efficient search
    priority = request.args.get("priority", default=0, type=int)
    all = request.args.get("all", default=False, type=bool)
    db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    priority_matrix = NegotiumCRUD(NegotiumModel, db).safe_execute(
        "get_priority_matrix", all=all
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
        priority=PRIORITY[priority],
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
        nid=nid,
    )


@negotium_blueprint.route("/vizchain/<int:nid>", methods=["GET"])
@protected
def viz_chain_by_nid(nid):
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


@negotium_blueprint.route("/update/<int:nid>", methods=["GET", "POST"])
@protected
def update_negotium(nid):
    db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    if request.method == "POST":
        fields = NegotiumCRUD.process_request_form(request)
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
        fields = NegotiumCRUD.process_request_form(request)
        db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
        instance = NegotiumCRUD(NegotiumModel, db).safe_execute("create", **fields)
        if instance is None:
            raise CustomException(400, "Negotium not created", "Bad request")
        return redirect(url_for("negotium.index"))
    # TODO consider adding to `NegotiumModel`
    instance = NegotiumModel.get_empty_instance(pid)
    return render_template(
        "negentry.html",
        logged_in=True,
        form_type="Create Negotium",
        can_submit=True,
        pid=pid,
        instance=instance,
    )


@negotium_blueprint.route("/link/<int:nid>", methods=["GET", "POST"])
@protected
def link_negotium(nid):
    if request.method == "POST":
        nid = int(request.form["nid"])
        blog_id = int(request.form["blog_id"])
        db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
        instance = NegBlogLinkerModel(blog_id=blog_id, negotium_id=nid)
        if instance is None:
            raise CustomException(400, "Negotium not created", "Bad request")
        return redirect(url_for("negotium.index"))
    return render_template(
        "neglinking.html",
        logged_in=True,
        form_type="Link Negotium",
        can_submit=True,
        nid=nid,
    )
