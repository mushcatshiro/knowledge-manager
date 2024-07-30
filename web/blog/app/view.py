import os

from flask import (
    Blueprint,
    render_template,
    current_app,
    request,
    send_from_directory,
)
import markdown
from sqlalchemy import create_engine

from blog import CustomException
from blog.bookmark import BookmarkModel
from blog.core import process_request
from blog.core.crud import CRUDBase
from blog.blogpost import (
    BlogPostModel,
    read_blog_post,
    read_blog_post_list,
    blogpost_name_helper,
    ImageURLlExtension,
)

main = Blueprint("main", __name__)

md = markdown.Markdown(extensions=["fenced_code", "tables", ImageURLlExtension()])


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
    **TODO
    ----
    - use database instead of os.listdir
    - deal with space in file name
    - date of blog
    - better filter i.e. non .md files
    """
    # blog_list = os.listdir(current_app.config["BLOG_PATH"])
    # output = []
    # for idx, _ in enumerate(blog_list):
    #     if blog_list[idx].endswith(".md"):
    #         output.append(blog_list[idx].replace(".md", ""))
    # for idx, _ in enumerate(blog_list):
    #     if blog_list[idx].endswith(".md"):
    #         output.append(blog_list[idx].replace(".md", ""))
    instances = read_blog_post_list(
        BlogPostModel,
        create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"]),
        current_app.config["PAGINATION_LIMIT"],
    )
    return render_template(
        "blog.html", blog_list=[x["title"] for x in instances], blog=True
    )


@main.route("/blog/<string:title>", methods=["GET"])
def blog_with_title(title):
    # blog_path = os.path.join(current_app.config["BLOG_PATH"], title + ".md")
    # if not os.path.exists(blog_path):
    #     content = f"Blog {title} not found!"
    # else:
    try:
        instance = read_blog_post(
            BlogPostModel,
            create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"]),
            title,
        )
        blog_path = os.path.join(
            current_app.config["BLOG_PATH"],
            blogpost_name_helper(
                instance["title"], instance["version"], instance["timestamp"]
            ),
        )
        # with open(blog_path, "r", encoding="utf-8") as rf:
        #     content = rf.read()
        with open(blog_path, "r", encoding="utf-8") as rf:
            content = rf.read()
            content = md.convert(content)
        return render_template("blog.html", content=content, blog=True)
    except CustomException as e:
        return render_template("blog.html", content=e.name, blog=True)


@main.route("/bookmarklet-list", methods=["GET"])
def bookmarklet_list():
    db = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
    page = request.args.get("page", 1, type=int)
    bookmarks_query_string = (
        "select * from bookmark order by timestamp desc "
        f"limit {current_app.config['PAGINATION_LIMIT'] * page} offset {current_app.config['PAGINATION_LIMIT'] * (page - 1)}"
    )
    total_length_query_string = "select count(*) as count from bookmark"

    basecrud = CRUDBase(BookmarkModel, db)
    instances = basecrud.safe_execute(
        operation="custom_query",
        query=bookmarks_query_string,
    )
    if not instances:
        raise CustomException(400, "No entry found", "No bookmark not created")
    total_length = basecrud.safe_execute(
        operation="custom_query",
        query=total_length_query_string,
    )[0]["count"]
    return render_template(
        "bookmarklet.html",
        bookmarks=instances,
        total=total_length,
        bookmarklet_list=True,
        has_prev=page > 1,
        has_next=total_length > page * current_app.config["PAGINATION_LIMIT"],
        prev_num=page - 1 if page > 1 else None,
        next_num=page + 1
        if total_length > page * current_app.config["PAGINATION_LIMIT"]
        else None,
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
    stmt = (
        "User-agent: *\n"
        "allow: /blog\n"
        "allow: /blog/*\n"
        "allow: /about\n"
        "disallow: /secured\n"
        "disallow: /secured/*\n"
    )
    return stmt
