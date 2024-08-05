import os

from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    current_app,
    session,
)
import markdown
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine

from blog import CustomException
from blog.auth import verify_token, protected
from blog.core.crud import CRUDBase
from blog.blogpost import (
    BlogPostModel,
    create_blog_post,
    read_blog_post_list,
    read_blog_post,
    update_blog_post,
    update_blog_post_model,
    blogpost_name_helper,
    ImageURLlExtension,
)


blogpost_blueprint = Blueprint("blogpost", __name__)

md = markdown.Markdown(extensions=["fenced_code", "tables", ImageURLlExtension()])


@blogpost_blueprint.route("/list", methods=["GET"])
def blog_list():
    logged_in = False
    if verify_token(session.get("token")):
        logged_in = True
    blog_list = read_blog_post_list(
        BlogPostModel,
        create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"]),
        pagination=current_app.config["PAGINATION_LIMIT"],
        logged_in=logged_in,
    )
    return render_template(
        "blog.html",
        blog_list=[x["title"] for x in blog_list],
        logged_in=logged_in,
    )


@blogpost_blueprint.route("/<string:title>", methods=["GET"])
def blog_with_title(title):
    logged_in = False
    if verify_token(session.get("token")):
        logged_in = True
    try:
        instance = read_blog_post(
            BlogPostModel,
            create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"]),
            title,
            logged_in=logged_in,
        )
        blog_path = os.path.join(
            current_app.config["BLOG_PATH"],
            blogpost_name_helper(
                instance["title"], instance["version"], instance["timestamp"]
            ),
        )
        with open(blog_path, "r", encoding="utf-8") as rf:
            content = rf.read()
            content = md.convert(content)
    except CustomException as e:
        content = e.name
    return render_template("blog.html", content=content, blog=True, logged_in=logged_in)


@blogpost_blueprint.route("/draft", methods=["GET", "POST"])
@protected
def draft():
    content = ""
    title = ""
    if request.method == "POST":
        content = request.form["content"]
        title = request.form["title"]
    return render_template(
        "draft.html",
        content=content,
        title=title,
        draft=True,
        logged_in=True,
        update=False,
    )


@blogpost_blueprint.route("/draft/<string:title>", methods=["GET", "POST"])
@protected
def draft_with_title(title):
    if request.method == "POST":
        content = request.form["content"]
        title = request.form["title"]
    else:
        instance = read_blog_post(
            BlogPostModel,
            create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"]),
            title,
            logged_in=True,
        )
        blog_path = os.path.join(
            current_app.config["BLOG_PATH"],
            blogpost_name_helper(
                instance["title"], instance["version"], instance["timestamp"]
            ),
        )
        with open(blog_path, "r", encoding="utf-8") as rf:
            content = rf.read()
    return render_template(
        "draft.html",
        content=content,
        title=title,
        draft=True,
        logged_in=True,
        update=True,
    )


@blogpost_blueprint.route("/preview", methods=["POST"])
@protected
def preview():
    content = request.form["content"]
    title = request.form["title"]
    converted_content = md.convert(content)
    return render_template(
        "preview.html",
        content=content,
        title=title,
        converted_content=converted_content,
        logged_in=True,
    )


@blogpost_blueprint.route("/save", methods=["POST"])
@protected
def save():
    # TODO handle update of title/filename and (un)private
    if request.form["update"] == "True":
        instance = update_blog_post(
            BlogPostModel,
            create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"]),
            request.form["content"].encode("utf-8"),
            request.form["title"],
            current_app.config["BLOG_PATH"],
        )
    else:
        instance = create_blog_post(
            BlogPostModel,
            create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"]),
            request.form["content"].encode("utf-8"),
            request.form["title"],
            current_app.config["BLOG_PATH"],
        )
    return redirect(url_for("blogpost.blog_with_title", title=instance["title"]))


@blogpost_blueprint.route("/upload", methods=["GET", "POST"])
@protected
def blog_upload():
    # TODO check box for document to be private
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
                    private=True if request.form.get("private") == "1" else False,
                )
            else:
                filename = secure_filename(file.filename)
                abs_path = os.path.join(current_app.config["BLOG_PATH"], filename)
                file.save(abs_path)
                os.chmod(abs_path, 0o644)
        return redirect(url_for("blogpost.blog_list"))
    return render_template("upload.html", logged_in=True)


@blogpost_blueprint.route("/edit/<string:title>", methods=["GET", "POST"])
@protected
def blog_model_edit_by_title(title):
    raise NotImplementedError("Not much use for BlogPostModel")
    if request.method == "POST":
        instance = update_blog_post_model(
            BlogPostModel,
            create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"]),
            blog_post_name=request.form["title"],
            version=request.form["version"],
            private=True if request.form.get("private") == "1" else False,
        )
        return redirect(url_for("blogpost.blog_list"))
    instance = read_blog_post(
        BlogPostModel,
        create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"]),
        title,
        logged_in=True,
        get_editable=True,
    )
    import logging

    logger = logging.getLogger(__name__)
    logger.debug(instance)
    return render_template("model_edit.html", instance=instance, logged_in=True)


@blogpost_blueprint.route("/export", methods=["GET", "POST"])
@protected
def blog_export():
    if request.method == "POST":
        # start thread to zip files
        return redirect(url_for("blogpost.blog_list"))
    # TODO list zip files
    return render_template("export.html", logged_in=True)
