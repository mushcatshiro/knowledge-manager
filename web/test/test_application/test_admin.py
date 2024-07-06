import io
import os

from blog.blogpost import blogpost_name_helper, read_blog_post, BlogPostModel

from flask import session


# TODO remove token in payload use session instead


def test_admin_route_before_request_handler(session_setup, auth_token, monkeypatch):
    """
    - w/o w/ token + login/non login
    - direct logout
    """
    _, test_app = session_setup
    client = test_app.test_client(use_cookies=True)

    response = client.get("/admin/fsrs/setup/cards")
    assert response.status_code == 302
    assert (
        response.location
        == "/admin/login?next=http%3A%2F%2Flocalhost%2Fadmin%2Ffsrs%2Fsetup%2Fcards"
    )

    response = client.get("/admin/fsrs/setup/cards", data={"token": "invalid"})
    assert response.status_code == 302
    assert (
        response.location
        == "/admin/login?next=http%3A%2F%2Flocalhost%2Fadmin%2Ffsrs%2Fsetup%2Fcards"
    )

    response = client.post("/admin/login", data={"token": "invalid"})
    assert response.status_code == 401
    assert b"Invalid token" in response.data

    with client:
        response = client.post(
            "/admin/login", data={"token": auth_token}, follow_redirects=True
        )
        assert response.status_code == 200
        assert session["token"] == auth_token

        response = client.get("/admin/fsrs/setup/cards")
        assert response.status_code == 200
        assert b"setup cards" in response.data

        # to test logout redirects to main.index
        # fail suspect due to context manager works in streaming mode
        response = client.get("/admin/logout", follow_redirects=True)
        assert response.status_code == 200
        assert "token" not in session

    client = test_app.test_client(use_cookies=True)

    with client:
        response = client.post(
            "/admin/login", data={"token": auth_token}, follow_redirects=True
        )
        monkeypatch.setattr("blog.admin.view.verify_token", lambda x: False)
        response = client.get("/admin/fsrs/setup/cards")
        assert response.status_code == 401


def test_upload_with_monkeypatch(
    session_setup, auth_token, monkeypatch, blogpost_db_cleanup
):
    _, test_app = session_setup
    client = test_app.test_client(use_cookies=True)
    monkeypatch.setattr("werkzeug.datastructures.FileStorage.save", lambda x, y: None)

    with client:
        response = client.post(
            "/admin/login", data={"token": auth_token}, follow_redirects=True
        )
        assert response.status_code == 200

        data = {"file": (io.BytesIO(b"abcdef"), "test.md"), "token": auth_token}
        response = client.post(
            "/admin/blog/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert response.status_code == 200

        data_no_file = {"token": auth_token}
        response = client.post(
            "/admin/blog/upload", data=data_no_file, content_type="multipart/form-data"
        )
        assert response.status_code == 400

        data_multi_file = {
            "file": [
                (io.BytesIO(b"abcdef"), "test1.md"),
                (io.BytesIO(b"abcdef"), "test2.md"),
            ],
            "token": auth_token,
        }
        response = client.post(
            "/admin/blog/upload",
            data=data_multi_file,
            content_type="multipart/form-data",
            follow_redirects=True,
        )


def test_upload_without_monkeypatch(
    session_setup, auth_token, cleanup_file, blogpost_db_cleanup
):
    engine, test_app = session_setup
    client = test_app.test_client(use_cookies=True)
    delete_list = cleanup_file

    with client:
        response = client.post(
            "/admin/login", data={"token": auth_token}, follow_redirects=True
        )
        assert response.status_code == 200

        data = {
            "file": (io.BytesIO(b"abcdef"), "test wo monkeypatch.md"),
            "token": auth_token,
        }
        response = client.post(
            "/admin/blog/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"test wo monkeypatch" in response.data
        instance = read_blog_post(BlogPostModel, engine, "test wo monkeypatch")
        fname = blogpost_name_helper(
            title=instance["title"],
            version=instance["version"],
            date=instance["timestamp"],
        )
        with open(os.path.join(test_app.config["BLOG_PATH"], fname), "r") as rf:
            assert rf.read() == "abcdef"
        print(fname)
        delete_list.append(fname)

    # test multiple files

    with client:
        response = client.post(
            "/admin/login", data={"token": auth_token}, follow_redirects=True
        )
        assert response.status_code == 200

        data = {
            "file": [
                (io.BytesIO(b"abcdef"), "test1.md"),
                (io.BytesIO(b"ghijk"), "test2.md"),
            ],
            "token": auth_token,
        }
        response = client.post(
            "/admin/blog/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"test1" in response.data
        assert b"test2" in response.data
        instance1 = read_blog_post(BlogPostModel, engine, "test1")
        instance2 = read_blog_post(BlogPostModel, engine, "test2")
        fname1 = blogpost_name_helper(
            title=instance1["title"],
            version=instance1["version"],
            date=instance1["timestamp"],
        )
        fname2 = blogpost_name_helper(
            title=instance2["title"],
            version=instance2["version"],
            date=instance2["timestamp"],
        )

        with open(os.path.join(test_app.config["BLOG_PATH"], fname1), "r") as rf:
            assert rf.read() == "abcdef"
        with open(os.path.join(test_app.config["BLOG_PATH"], fname2), "r") as rf:
            assert rf.read() == "ghijk"
        print(fname1, fname2)
        delete_list.append(fname1)
        delete_list.append(fname2)


def test_upload_with_image(
    session_setup, auth_token, cleanup_file, blogpost_db_cleanup
):
    pass


def test_save_endpoint(session_setup, auth_token, cleanup_file):
    engine, test_app = session_setup
    client = test_app.test_client(use_cookies=True)
    delete_list = cleanup_file

    with client:
        response = client.post(
            "/admin/login", data={"token": auth_token}, follow_redirects=True
        )
        assert response.status_code == 200

        data = {"title": "test", "content": "abcdef", "token": auth_token}
        response = client.post("/admin/save", data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b"abcdef" in response.data
        instance = read_blog_post(BlogPostModel, engine, "test")
        fname = blogpost_name_helper(
            title=instance["title"],
            version=instance["version"],
            date=instance["timestamp"],
        )
        print(fname)
        delete_list.append(fname)
