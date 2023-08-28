from flask import Blueprint, request, render_template, session, redirect
from urllib.parse import quote_plus

from blog import sess
from blog.auth import verify_token


admin = Blueprint("admin", __name__)


@admin.before_request
def before_request_handler():
    if "token" not in session:
        return redirect("/admin/login?next={}".format(quote_plus(request.url)))


@admin.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and verify_token(request.form["token"]):
        sess["token"] = request.form["token"]
        next = request.args.get("next", "/")
        return redirect(next)
    return render_template("login.html")


@admin.route("/fsrs/setup/cards", methods=["GET", "POST"])
def fsrs_setup_cards():
    return "setup cards"


@admin.route("/fsrs/setup/configs", methods=["GET", "POST"])
def fsrs_setup_configs():
    pass


@admin.route("/fsrs/review", methods=["GET", "POST"])
def fsrs_review():
    pass