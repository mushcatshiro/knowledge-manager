import os
from urllib.parse import quote_plus

from flask import (
    Blueprint,
    request,
    render_template,
    session,
    redirect,
    url_for,
    current_app,
)
import markdown

from blog import sess, db
from blog.auth import verify_token
from blog.core.crud import CRUDBase


admin = Blueprint("admin", __name__)

md = markdown.Markdown(extensions=["fenced_code", "tables"])


@admin.before_request
def before_request_handler():
    if "token" not in session:
        return redirect(f"/admin/login?next={quote_plus(request.url)}")


@admin.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and verify_token(request.form["token"]):
        sess["token"] = request.form["token"]
        next_url = request.args.get("next", "/")
        return redirect(next_url)
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


@admin.route("/draft", methods=["GET", "POST"])
def draft():
    content = ""
    title = ""
    if request.method == "POST":
        content = request.form["content"]
        title = request.form["title"]
    return render_template("draft.html", content=content, title=title, draft=True)


@admin.route("/save", methods=["POST"])
def save():
    if verify_token(request.form["token"]):
        blog_root = current_app.config["BLOG_PATH"]
        blog_title = request.form["title"]
        with open(
            os.path.join(blog_root, f"{blog_title}.md"), "w", encoding="utf-8"
        ) as wf:
            wf.write(request.form["content"])
        return redirect(url_for("main.blog"))
    raise Exception("Invalid token")


@admin.route("/preview", methods=["POST"])
def preview():
    content = request.form["content"]
    title = request.form["title"]
    converted_content = md.convert(content)
    return render_template(
        "preview.html",
        content=content,
        title=title,
        converted_content=converted_content,
    )


@admin.route("/edit/<string:modelname>", methods=["POST"])
def edit(modelname):
    basecrud = CRUDBase(modelname, db)
    instance = basecrud.execute(
        operation="update",
        id=request.form["id"],
        title=request.form["title"],
        url=request.form["url"],
        img=request.form["img"],
        desc=request.form["desc"],
    )
    return instance
