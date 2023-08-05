from flask import Blueprint, jsonify, request, current_app, url_for
import datetime as dt
import os

# from blog.models import Bookmark
from blog.auth import verify_token
from utils.database import PostgresConx

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