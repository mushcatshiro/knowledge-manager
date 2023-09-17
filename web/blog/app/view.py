from flask import (
    Blueprint,
    render_template,
    current_app,
    request,
    send_from_directory,
    redirect,
    url_for,
)
import os
import markdown

from blog import db
from blog.auth import verify_token
from blog.bookmark import BookmarkModel
from blog.core import process_request
from blog.core.crud import CRUDBase

main = Blueprint("main", __name__)

md = markdown.Markdown(extensions=["fenced_code", "tables"])


@main.route("/", methods=["GET", "POST"])
def index():
    """
    TODO
    ----
    - handle payload schema (validation and error handling)
      - handle at hook level or through a decorator
    - permission handling for certain fns
    - alternative to return resp as a string/html string
      - or having multiple templates for different responses
    """
    if request.method == "POST":
        resp = process_request(request.form["query"])
        return render_template("main.html", resp=resp)
    return render_template("main.html")


@main.route("/about", methods=["GET"])
def about():
    return render_template("about.html", about=True)


@main.route("/blog", methods=["GET"])
def blog():
    """
    TODO
    ----
    - use database instead of os.listdir
    - deal with space in file name
    - date of blog
    - better filter i.e. non .md files
    """
    blog_path = current_app.config["BLOG_PATH"]
    blog_list = os.listdir(blog_path)
    output = []
    for i in range(len(blog_list)):
        if blog_list[i].endswith(".md"):
            output.append(blog_list[i].replace(".md", ""))
    return render_template("blog.html", blog_list=output, blog=True)


@main.route("/blog/<string:title>", methods=["GET"])
def blog_with_title(title):
    blog_path = os.path.join(current_app.config["BLOG_PATH"], title + ".md")
    if not os.path.exists(blog_path):
        content = f"Blog {title} not found!"
    else:
        with open(blog_path, "r", encoding="utf-8") as f:
            content = f.read()
            content = md.convert(content)
    return render_template("blog.html", content=content, blog=True)


@main.route("/draft", methods=["GET", "POST"])
def draft():
    content = ""
    title = ""
    if request.method == "POST":
        content = request.form["content"]
        title = request.form["title"]
    return render_template("draft.html", content=content, title=title, draft=True)


@main.route("/save", methods=["POST"])
def save():
    if verify_token(request.form["token"]):
        blog_root = current_app.config["BLOG_PATH"]
        blog_title = request.form["title"]
        with open(
            os.path.join(blog_root, f"{blog_title}.md"), "w", encoding="utf-8"
        ) as f:
            f.write(request.form["content"])
        return redirect(url_for("main.blog"))
    else:
        raise Exception("Invalid token")


@main.route("/preview", methods=["POST"])
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


@main.route("/bookmarklet-list", methods=["GET"])
def bookmarklet_list():
    # page = request.args.get('page', 1, type=int)
    query_string =\
    "select * from bookmark "\
    "order by timestamp desc "\
    # f"limit {100 * page} offset {100 * (page - 1)}"

    basecrud = CRUDBase(BookmarkModel, db)
    instances = basecrud.execute(
        operation="custom_query",
        query=query_string,
    )
    if not instances:
        raise Exception("Bookmark not created")
    return render_template(
        "bookmarklet.html",
        bookmarks=[instance.to_json() for instance in instances],
        total=len(instances),
        bookmarklet_list=True,
    )


@main.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@main.route("/robots.txt")
def robots():
    stmt =\
    "User-agent: *\n"\
    "allow: /blog\n"\
    "allow: /about\n"
    return stmt