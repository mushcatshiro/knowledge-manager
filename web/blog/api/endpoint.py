from flask import Blueprint, jsonify, request, current_app, url_for
import datetime as dt
import os
import time

# from blog.models import Bookmark
from blog.auth import verify_token
from utils.database import PostgresConx
from utils.healthcheck import server_healthcheck

api = Blueprint("api", __name__)


@api.route("/bookmark", methods=["GET"])
def bookmark():
    payload = request.args.to_dict()
    if verify_token(payload["token"]):
        payload["timestamp"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_app.logger.info(payload)
        return jsonify({"status": "success", "payload": payload})
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