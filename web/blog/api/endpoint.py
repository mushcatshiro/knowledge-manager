from flask import Blueprint, jsonify, request, current_app, url_for

from utils.database import PostgresConx

api = Blueprint("api", __name__)


@api.route("/mock", methods=["GET"])
def mock():
    return jsonify([
        {
            "title": "optimization",
            "url": "www.example.com",
            "desc": "optimization is interesting!"
        },
        {
            "title": "distributed systems",
            "url": "www.example.com",
            "desc": "distributed system is fun"
        }
    ])

@api.route("/reading_list", methods=["POST"])
def reading_list():
    payload = request.json
    p = PostgresConx(
        current_app.config["DSN"],
        "SELECT page_title, url, description FROM history",
        "QUERY",
        None
    )
    ret, error = p.run()
    if not error:
        return jsonify(ret)

@api.route("/detail")
def detail():
    return jsonify({
        "text": "lorem"
    })


@api.route("/image", methods=["POST"])
def image():
    payload = request.json
    fname = payload["probe"] + ".webp"
    return jsonify({"url": url_for("static", filename=fname)})

"""
@api.route("/auth", methods=["POST"])
def auth():
    payload = request.json
    if payload["auth"] == current_app.config["auth"]:
        return current_app.config[""]
"""