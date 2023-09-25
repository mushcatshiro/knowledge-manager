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

from blog import db, CustomException
from blog.auth import verify_token
from blog.core.crud import CRUDBase


admin = Blueprint("admin", __name__)

md = markdown.Markdown(extensions=["fenced_code", "tables"])


@admin.before_request
def before_request_handler():
    """
    TODO
    ---
    - check token expiry
    """
    if not session.get("token"):
        # TODO with token and yet going to login route?
        return redirect(f"/admin/login?next={quote_plus(request.url)}")
    if not verify_token(session.get("token")):
        session.pop("token")
        raise CustomException(401, "unauthorized access", "unauthorized access")


@admin.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if verify_token(request.form["token"]):
            session["token"] = request.form["token"]
            next_url = request.args.get("next", "/")
            return redirect(next_url)
        raise CustomException(400, "Invalid token", "Invalid token")
    return render_template("login.html")


@admin.route("/logout", methods=["GET"])
def logout():
    session.pop("token")
    return redirect("/")


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


@admin.route("/bookmarkletjs", methods=["GET"])
def bookmarkletjs():
    script = [
        "javascript:(() => {",
        f'const requestURL = "{current_app.config["SITE_BASE_URL"]}/api/bookmark";',
        "const pageTitle = document.title;",
        "const pageURL = window.location.href;",
        'let metaImage = "";',
        'let metaDescription = "";',
        f'let token = "{session.get("token")}";',
        "function getMetaValue(propName) {",
        'const x = document.getElementsByTagName("meta");',
        "for (let i = 0; i < x.length; i++) {",
        "const y = x[i];",
        "let metaName;",
        "if (y.attributes.property !== undefined) {",
        "metaName = y.attributes.property.value;}",
        "if (y.attributes.name !== undefined) {",
        "metaName = y.attributes.name.value;}",
        "if (metaName === undefined) {continue;}",
        "if (metaName === propName) {return y.attributes.content.value;}}",
        "return undefined;}",
        '{let desc = getMetaValue("og:description");',
        "if (desc !== undefined) {metaDescription = desc;}",
        'else {desc = getMetaValue("description");',
        "if (desc !== undefined) {metaDescription = desc;}}}",
        '{const img = getMetaValue("og:image");',
        "if (img !== undefined) {metaImage = img;}}",
        'console.log("BOOKMARKET PRESSED:", pageTitle, pageURL, metaDescription, metaImage);',
        "const url = new URL(requestURL);",
        "const searchParams = url.searchParams;",
        'searchParams.set("title", pageTitle);',
        'searchParams.set("url", pageURL);',
        'searchParams.set("desc", metaDescription);',
        'searchParams.set("img", metaImage);',
        'searchParams.set("token", token);',
        "window.location.href = url; })();"
    ]
    return render_template(
        "bookmarkletjs.html",
        script=script.join("") if request.args.get("min") else script.join("\n")
    )
