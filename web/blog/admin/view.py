import os

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
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine

from blog import CustomException
from blog.auth import verify_token
from blog.core.crud import CRUDBase
from blog.blogpost import (
    BlogPostModel,
    create_blog_post,
    update_blog_post,
    delete_blog_post,
)


admin = Blueprint("admin", __name__)

md = markdown.Markdown(extensions=["fenced_code", "tables"])


@admin.before_request
def before_request_handler():
    """
    TODO
    ---
    - check token expiry
    """
    if request.path == "/admin/login":
        pass
    elif not session.get("token"):
        return redirect(url_for("admin.login", next=request.url))
    elif not verify_token(session.get("token")):
        session.pop("token")
        raise CustomException(401, "Invalid token", "Unauthorized access")


@admin.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if verify_token(request.form["token"]):
            session["token"] = request.form["token"]
            next_url = request.args.get("next", "/")
            return redirect(next_url)
        raise CustomException(401, "Invalid token", "Unauthorized access")
    return render_template("login.html")


@admin.route("/logout", methods=["GET"])
def logout():
    session.pop("token")
    return redirect(url_for("main.index"))


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
    if verify_token(request.form["token"]):  # TODO remove
        intance = create_blog_post(
            BlogPostModel,
            create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"]),
            request.form["content"].encode("utf-8"),
            request.form["title"],
            current_app.config["BLOG_PATH"],
        )
        return redirect(url_for("main.blog_with_title", title=intance["title"]))
    raise CustomException(401, "Invalid token", "Invalid token")  # TODO remove


@admin.route("/blog/upload", methods=["GET", "POST"])
def blog_upload():
    if request.method == "POST":
        if "file" not in request.files:
            raise CustomException(400, "No file part", "Invalid request")
        payload = request.files["file"]
        if payload.filename == "":
            raise CustomException(400, "No file name", "Invalid request")
        files = request.files.getlist("file")
        for file in files:
            if (
                file.filename.split(".")[-1]
                not in current_app.config["ALLOWED_EXTENSIONS"]
            ):
                continue
            # check file size
            if file.content_length > current_app.config["MAX_CONTENT_LENGTH"]:
                continue
            if file.filename.endswith(".md"):
                instance = create_blog_post(
                    BlogPostModel,
                    create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"]),
                    file.read(),
                    file.filename.replace(".md", ""),
                    current_app.config["BLOG_PATH"],
                )
            else:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config["BLOG_PATH"], filename))
        return redirect(url_for("main.blog"))
    return render_template("upload.html")


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
    db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    basecrud = CRUDBase(modelname, db)
    instance = basecrud.safe_execute(
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
        "window.location.href = url; })();",
    ]
    return render_template(
        "bookmarkletjs.html",
        script="".join(script)
        if request.args.get("min")
        else "\n".join(script),  # BUG test needed
    )


@admin.route("/schedule")
def schedule():
    """
    default get overdue + look ahead 14 days + critical items
    option to use date picker to move around with default?
    """


@admin.route("/schedule/create", methods=["GET", "POST"])
def create_schedule():
    pass


@admin.route("/schedule/edit/<int:sid>", methods=["GET", "POST"])
def edit_schedule(sid):
    """
    no hard delete, just update delete flag
    """


@admin.route("/negotium/preview")
def negotium_preview():
    return render_template("negotium.html")
