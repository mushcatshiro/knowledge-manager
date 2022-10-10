from flask import Blueprint, jsonify, request, current_app, url_for

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

'''
@api.route("/auth", methods=["POST"])
def auth():
    payload = request.json
    if payload["auth"] == current_app.config["auth"]:
        return current_app.config[""]
'''