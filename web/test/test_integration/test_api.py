import random


def test_api_bookmark(test_app, auth_token):
    """
    TODO
    ----
    obviously its not consistent for an api's error response to be html
    """
    client = test_app.test_client()
    s1 = str(random.random())[2:]
    response = client.get(
        bookmark_url_helper(auth_token, s1, f"http://{s1}.com", "img", "desc")
    )
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["payload"]["title"] == s1

    response = client.get(
        bookmark_url_helper(auth_token, s1, f"http://{s1}.com", "img", "desc")
    )
    assert response.status_code == 400
    # assert "Bookmark already exists" in response.text

    s2 = str(random.random())[2:]
    response = client.get(
        bookmark_url_helper("invalid_token", s2, f"http://{s2}.com", "img", "desc")
    )
    assert response.status_code == 400
    # assert "Invalid token" in response.text


def bookmark_url_helper(token, title, url, img, desc):
    return f"/api/bookmark?token={token}&title={title}&url={url}&img={img}&desc={desc}"
