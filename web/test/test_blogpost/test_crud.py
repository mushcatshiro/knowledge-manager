from blog.blogpost import BlogPostModel, BlogPostCrud

import pytest


def test_create(blogpost_db):
    basecrud = BlogPostCrud(BlogPostModel, blogpost_db)
    with pytest.raises(FileExistsError):
        basecrud.execute("create_blog_post", title="test title 1")
    assert (
        basecrud.execute("create_blog_post", title="test title 2")["title"]
        == "test title 2"
    )


def test_read(blogpost_db):
    basecrud = BlogPostCrud(BlogPostModel, blogpost_db)
    assert (
        basecrud.execute("read_blog_post", title="test title 1")["title"]
        == "test title 1"
    )
    # deleted
    with pytest.raises(FileNotFoundError):
        basecrud.execute("read_blog_post", title="test title -1")
    # dne
    with pytest.raises(ValueError):
        basecrud.execute("read_blog_post", title="test title -2")

    assert len(basecrud.execute("read_blog_post_list")) == 2


def test_update(blogpost_db):
    basecrud = BlogPostCrud(BlogPostModel, blogpost_db)
    assert basecrud.execute("update_blog_post", title="test title 1")["version"] == 2
    assert (
        basecrud.execute(
            "custom_query",
            query="select count(*) as count from blog_post where title = 'test title 1'",
        )[0]["count"]
        == 2
    )
    # dne entry
    with pytest.raises(ValueError):
        basecrud.execute("update_blog_post", title="test title -2")
    # deleted entry
    with pytest.raises(FileNotFoundError):
        basecrud.execute("update_blog_post", title="test title -1")


def test_delete(blogpost_db):
    basecrud = BlogPostCrud(BlogPostModel, blogpost_db)
    assert basecrud.execute("delete_blog_post", title="test title 0")
    assert (
        basecrud.execute(
            "custom_query",
            query="select distinct(deleted) as dist from blog_post where title = 'test title 0'",
        )[0]["dist"]
        == 1
    )
    # dne entry
    with pytest.raises(ValueError):
        basecrud.execute("delete_blog_post", title="test title -2")
    # deleted entry
    assert basecrud.execute("delete_blog_post", title="test title -1")
