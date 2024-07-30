import markdown

from blog.blogpost import ImageURLlExtension


def test_image_url_extension():
    import os

    os.environ["IMAGE_URL_PREFIX"] = "static"  # bypass
    md = markdown.Markdown(extensions=["fenced_code", "tables", ImageURLlExtension()])

    content = md.convert("![alt text](./image.png)")
    assert content == '<p><img alt="alt text" src="../static/image.png" /></p>'
