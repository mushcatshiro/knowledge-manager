import os


def create_blogpost(tmpl_dir, blogpost_dir, **kwargs):
    """ """
    assert os.path.isdir(tmpl_dir) and os.path.isabs(tmpl_dir)
    assert os.path.isabs(blogpost_dir)

    if not os.path.isdir(blogpost_dir):
        pass

    return
