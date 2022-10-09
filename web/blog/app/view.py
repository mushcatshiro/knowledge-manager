from flask import Blueprint, render_template


main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    return render_template("main.html")