from flask import Blueprint, jsonify, request, current_app
import jwt

auth = Blueprint("auth", __name__)


def verify_token(token):
    try:
        _ = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        return True
    except Exception:
        return False


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
    if not verify_token(request.json["token"]):
        return jsonify({"status": "failed", "token": request.json["token"]})
    return jsonify({"status": "success", "token": request.json["token"]})
