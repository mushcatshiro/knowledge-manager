import os
import logging
from urllib.parse import unquote

from blog import CustomException
from .crud import BlogPostCrud


logger = logging.getLogger(__name__)


def blogpost_name_helper(title: str, version: int, date: str) -> str:
    """
    unix time stamp
    """
    if not title:
        raise ValueError("Title cannot be empty")
    return f"{'-'.join(title.split(' '))}-{version}-{date}.md".replace(":", "-")


def create_blog_post(
    model, db, blog_post: bytes, blog_post_name: str, storage_path: str
):
    # images?
    basecrud = BlogPostCrud(model, db)
    try:
        instance = basecrud.execute("create_blog_post", title=blog_post_name)
    except FileExistsError:
        instance = basecrud.execute("update_blog_post", title=blog_post_name)
    except Exception as e:
        logger.error(e)  # get more details
        return None

    blog_post_fname = blogpost_name_helper(
        title=blog_post_name,
        version=instance["version"],
        date=instance["timestamp"],
    )
    # save blog post to file system
    abs_path = os.path.join(storage_path, blog_post_fname)
    with open(abs_path, "wb") as wf:
        wf.write(blog_post)
    return instance


def read_blog_post(model, db, blog_post_name: str):
    # handle dne and deleted separately
    # handle %20
    blog_post_name = unquote(blog_post_name)
    basecrud = BlogPostCrud(model, db)
    try:
        instance = basecrud.execute("read_blog_post", title=blog_post_name)
    except ValueError:
        raise CustomException(
            404, "Not found", f"Blog post {blog_post_name} not found!"
        )
    except FileNotFoundError:
        raise CustomException(410, "Gone", "Blog post deleted")
    # instance should be limited to necessary fields
    return instance


def read_blog_post_list(model, db, pagination):
    basecrud = BlogPostCrud(model, db)
    instance = basecrud.execute("read_blog_post_list")
    return instance


def update_blog_post(
    model, db, blog_post: bytes, blog_post_name: str, storage_path: str
):
    # return instance should help redirect to updated blog post
    # images?
    basecrud = BlogPostCrud(model, db)
    instance = basecrud.execute("update_blog_post", title=blog_post_name)
    blog_post_fname = blogpost_name_helper(
        title=blog_post_name,
        version=instance.version,
        date=instance.timestamp,
    )
    # update blog post file
    with open(os.path.join(storage_path, blog_post_fname), "wb") as wf:
        wf.write(blog_post)
    return instance


def delete_blog_post(model, db, blog_post_name: str):
    basecrud = BlogPostCrud(model, db)
    instance = basecrud.execute("delete_blog_post", title=blog_post_name)
    return instance


def diff_blog_post():
    pass
