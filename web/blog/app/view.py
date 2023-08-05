from flask import Blueprint, render_template, current_app
import os

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def index():
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
    for i in range(len(blog_list)):
        blog_list[i] = blog_list[i].replace(".md", "")
    return render_template("blog.html", blog_list=blog_list, blog=True)

@main.route("/blog/<string:title>", methods=["GET"])
def blog_with_title(title):
    blog_path = os.path.join(current_app.config["BLOG_PATH"], title+".md")
    if not os.path.exists(blog_path):
        content = f"Blog {title} not found!"
    else:
        with open (blog_path, "r", encoding="utf-8") as f:
            content = f.readlines()
    return render_template("blog.html", content=content, blog=True)

@main.route("/notes", methods=["GET"])
def notes():
    return render_template("notes.html", notes_list=[], notes=True)

@main.route("/notes/<string:title>", methods=["GET"])
def notes_with_title(title):
    return render_template("notes.html", content="no content yet", notes=True)

@main.route("/admin")
def admin():
    pass