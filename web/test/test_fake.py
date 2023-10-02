from blog.bookmark import BookmarkModel
from blog.utils.fake import create_fake_data


def test_create_fake_data():
    num = 10
    instance = create_fake_data(BookmarkModel, num=10)
    assert len(instance) == 10
