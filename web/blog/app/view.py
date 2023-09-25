import os

from flask import (
    Blueprint,
    render_template,
    current_app,
    request,
    send_from_directory,
)
import markdown

from blog import db
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
    blog_list = os.listdir(current_app.config["BLOG_PATH"])
    output = []
    for idx, _ in enumerate(blog_list):
        if blog_list[idx].endswith(".md"):
            output.append(blog_list[idx].replace(".md", ""))
    return render_template("blog.html", blog_list=output, blog=True)


@main.route("/blog/<string:title>", methods=["GET"])
def blog_with_title(title):
    blog_path = os.path.join(current_app.config["BLOG_PATH"], title + ".md")
    if not os.path.exists(blog_path):
        content = f"Blog {title} not found!"
    else:
        with open(blog_path, "r", encoding="utf-8") as rf:
            content = rf.read()
            content = md.convert(content)
    return render_template("blog.html", content=content, blog=True)


@main.route("/bookmarklet-list", methods=["GET"])
def bookmarklet_list():
    # page = request.args.get('page', 1, type=int)
    query_string = "select * from bookmark order by timestamp desc"  # f"limit {100 * page} offset {100 * (page - 1)}"

    basecrud = CRUDBase(BookmarkModel, db)
    instances = basecrud.execute(
        operation="custom_query",
        query=query_string,
    )
    if not instances:
        raise Exception("Bookmark not created")
    return render_template(
        "bookmarklet.html",
        bookmarks=instances,
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


@main.route("/secured", methods=["GET", "POST"])
def secured():
    return


@main.route("/secured/<string:value>", methods=["GET"])
def secured_with_value(value):
    return


@main.route("/robots.txt")
def robots():
    stmt =\
        "User-agent: *\nallow: /blog\nallow: /blog/*\n allow: /about\n"\
        "disallow: /secured\ndisallow: /secured/*\n"
    return stmt
