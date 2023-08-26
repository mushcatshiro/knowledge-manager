from flask import Blueprint, jsonify, request
import datetime as dt

from blog.bookmark import BookmarkModel
from blog.auth import verify_token
from blog.core.crud import CRUDBase
from blog.utils.healthcheck import server_healthcheck
from blog import db

api = Blueprint("api", __name__)


@api.route("/bookmark", methods=["GET"])
def bookmark():
    payload = request.args.to_dict()
    if verify_token(payload["token"]):
        payload.pop("token")
        basecrud = CRUDBase(BookmarkModel, db)
        instance: BookmarkModel = basecrud.execute(
            operation="create",
            **payload
        )
        if not instance:
            raise Exception("Bookmark not created")
        return jsonify({"status": "success", "payload": instance.to_json()})
    else:
        raise Exception("Invalid token")

@api.route("/healthcheck", methods=["GET"])
def healthcheck():
    """
    - Add database healthcheck
    - Add redis healthcheck
    - Add celery healthcheck
    """
    payload = {
        "timestamp": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": None,
        "message": None,
    }
    try:
        health = server_healthcheck()
    except Exception as e:
        payload["status"] = "error"
        payload["message"] = str(e)
    else:
        payload["status"] = "success"
        payload.update(health)
    return jsonify(payload)