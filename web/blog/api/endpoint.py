import datetime as dt
from threading import Thread

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import create_engine

from blog.bookmark import BookmarkModel
from blog.auth import verify_token
from blog.core.crud import CRUDBase
from blog.utils.healthcheck import server_healthcheck
from blog import CustomException


api = Blueprint("api", __name__)


@api.route("/bookmark", methods=["GET"])
def bookmark():
    """
    TODO
    ----
    - redirect to bookmark page
    """
    payload = request.args.to_dict()
    if verify_token(payload["token"]):
        db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
        payload.pop("token")
        basecrud = CRUDBase(BookmarkModel, db)
        instance: BookmarkModel = basecrud.safe_execute(operation="create", **payload)
        if not instance:
            raise CustomException(400, "Bookmark not created", "Bad request")
        return jsonify({"status": "success", "payload": instance})
    raise CustomException(401, "Invalid token", "Unauthorized access")


@api.route("/healthcheck", methods=["GET"])
def healthcheck():
    """
    - Add database healthcheck
    - Add redis healthcheck
    - Add celery healthcheck
    - run as async task
    - add a view to show historical trend
    """
    if not verify_token(request.args.get("token")):
        raise Exception("Invalid token")
    if request.args.get("user") == "cron":
        Thread(target=server_healthcheck, kwargs={"to_db": True}).start()
        return jsonify(
            {"message": f"triggered server healthcheck at {dt.datetime.now()}"}
        )
    return server_healthcheck(False, None)
