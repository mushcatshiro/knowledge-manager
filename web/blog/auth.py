from flask import Blueprint, jsonify, request, current_app
import jwt

auth = Blueprint("auth", __name__)


def verify_token(token):
    try:
        decoded_jwt = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return True
    except:
        return False

@auth.route("/auth", methods=["POST"])
def auth():
    payload = request.json
    if payload["auth"] == current_app.config["auth"]:
        encoded_jwt = jwt.encode(
            {"auth": current_app.config["auth"]},
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        return current_app.config[""]

@auth.route("/token", methods=["POST"])
def token():
    payload = request.json
    if payload["auth"] == current_app.config["auth"]:
        return current_app.config[""]