import os

from blog.blogpost import (
    BlogPostModel,
    create_blog_post,
    read_blog_post,
    read_blog_post_list,
    update_blog_post,
    delete_blog_post,
    blogpost_name_helper,
)


def test_blog_post_name_helper():
    # handling special char
    # handling empty string
    pass


def test_create_blog_post(session_setup, blogpost_db, cleanup_blog, monkeypatch):
    _, test_app = session_setup
    delete_list = cleanup_blog
    blog_post_name = "testing"

    instance = create_blog_post(
        BlogPostModel,
        blogpost_db,
        b"test",
        blog_post_name,
        test_app.config["BLOG_PATH"],
    )
    blogname = blogpost_name_helper(
        instance["title"], instance["version"], instance["timestamp"]
    )
    delete_list.append(blogname)
    assert instance["version"] == 1
    assert blogname in os.listdir(test_app.config["BLOG_PATH"])

    instance = create_blog_post(
        BlogPostModel,
        blogpost_db,
        b"test",
        blog_post_name,
        test_app.config["BLOG_PATH"],
    )
    blogname = blogpost_name_helper(
        instance["title"], instance["version"], instance["timestamp"]
    )
    delete_list.append(blogname)
    assert instance["version"] > 1
    assert blogname in os.listdir(test_app.config["BLOG_PATH"])

    def mock_create_blog_post(*args, **kwargs):
        raise Exception

    monkeypatch.setattr(
        "blog.blogpost.BlogPostCrud.create_blog_post", mock_create_blog_post
    )
    instance = create_blog_post(
        BlogPostModel,
        blogpost_db,
        b"test",
        blog_post_name,
        test_app.config["BLOG_PATH"],
    )
    assert instance is None


def test_read_blog_post(blogpost_db):
    # test get specific blog post -> not tested, wrapper for crud
    # test get non existing blog post -> not tested, wrapper for crud

    # test get specific blog post version, behind auth for api
    pass


def test_read_blog_post_list():
    # test get list of blog post -> not tested, wrapper for crud
    # test get list of blog post with pagination
    pass


def test_delete_blog_post():
    # test delete existing blog post -> not tested, wrapper for crud
    # test delete non existing blog post -> not tested, wrapper for crud
    pass


def test_update_blog_post():
    # test update existing blog post
    # test update non existing blog post
    pass


def test_export_import_blog_post():
    # test export existing blog post
    # test export non existing blog post
    pass


def test_sync_blog_post():
    pass


def test_sync_local_to_remote():
    pass
