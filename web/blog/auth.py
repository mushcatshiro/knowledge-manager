from functools import wraps

from flask import Blueprint, jsonify, request, current_app, session
import jwt

from blog import CustomException

auth = Blueprint("auth", __name__)


def verify_token(token):
    try:
        _ = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return True
    except Exception:
        return False


def protected(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        token = session.get("token")
        if not token:
            raise CustomException(401, "Token not found", "Unauthorized access")
        if not verify_token(token):
            raise CustomException(401, "Invalid token", "Unauthorized access")
        return f(*args, **kwargs)

    return decorated_view


@auth.route("/authenticate", methods=["POST"])
def authenticate():
    if request.json["auth"] == current_app.config["AUTH"]:
        encoded_jwt = jwt.encode(
            {
                "auth": current_app.config["AUTH"],
                # "exp": current_app.config["EXPIRE_AFTER_SECS"],
                # "path": current_app.config["BLOG_PAT"]
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return jsonify({"status": "success", "token": encoded_jwt})
    return jsonify({"status": "failed", "token": None})


@auth.route("/token", methods=["POST"])
def token():
    # TODO remove?
    if not verify_token(request.json["token"]):
        return jsonify({"status": "failed", "token": request.json["token"]})
    return jsonify({"status": "success", "token": request.json["token"]})
