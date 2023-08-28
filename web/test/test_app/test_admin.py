def test_before_request_handler(test_app):
    client = test_app.test_client(use_cookies=True)
    response = client.get("/admin/fsrs/setup/cards")
    assert response.status_code == 302
    assert response.location == "/admin/login?next=http%3A%2F%2Flocalhost%2Fadmin%2Ffsrs%2Fsetup%2Fcards"