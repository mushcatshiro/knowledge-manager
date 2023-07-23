from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def index():
    return render_template("main.html")

@main.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@main.route("/blog/<title:str>", methods=["GET"])
def blog(title):
    return render_template("blog.html")

@main.route("/notes/<title:str>", methods=["GET"])
def notes(title):
    return render_template("notes.html")

@main.route("/admin")
def admin():
    pass