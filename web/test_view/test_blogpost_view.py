import pytest

from playwright.sync_api import Page, expect

from .commons import clear_session, setup_auth_session


@pytest.fixture(scope="module")
def upload_documents(context, page: Page, new_context):
    # public upload
    files = ["fname", "fname1"]
    setup_auth_session(page)
    page.goto("/blog/upload")
    page.locator("#description").fill("test")
    page.get_by_label("File(s)").set_input_files([files[0]])
    page.get_by_role("button", name="Upload").click()

    # private upload
    page.goto("/blog/upload")
    page.locator("#description").fill("test")
    page.get_by_label("Private").check()
    page.get_by_label("File(s)").set_input_files([files[1]])
    page.get_by_role("button", name="Upload").click()
    yield files


def test_blog_list(page: Page, upload_documents):
    files = upload_documents
    page.goto("/blog/list")
    expect(page.locator("body")).to_contain_text(f"{files[0]} edit as draft edit model")
    expect(page.locator("body")).to_contain_text(f"{files[1]} edit as draft edit model")
    clear_session(page)

    page.goto("/blog/list")
    expect(page.locator("body")).to_contain_text(files[0])
    with pytest.raises(Exception):
        expect(page.locator("body")).to_contain_text(files[1])


def test_blog_with_title(page: Page, upload_documents):
    files = upload_documents
    clear_session(page)
    page.goto(f"/blog/{files[0]}")
    expect(page.locator("body")).to_contain_text(files[0])


def test_edit_as_draft_preview_save(page: Page, upload_documents):
    files = upload_documents
    page.goto("/blog/list")
    page.locator(f"xpath=.//a[contains(@href, '/blog/draft/{files[1]}')]").click()
    expect(page.get_by_label("Is Update?")).to_have_value("True")
    page.get_by_label("Content").fill("test")
    page.get_by_role("button", name="Preview").click()
    expect(page.locator("body")).to_contain_text("test")
    page.get_by_role("button", name="Back to edit").click()
    page.get_by_role("button", name="Save").click()
    expect(page.locator("body")).to_contain_text("test")
    clear_session(page)
    page.goto(f"/blog/{files[1]}")
    with pytest.raises(Exception):
        expect(page.locator("body")).to_contain_text("test")


def test_new_draft_with_title_preview_save(page: Page):
    setup_auth_session(page)
    page.goto("/blog/draft")
    expect(page.get_by_label("Is Update?")).to_have_value("False")
    page.get_by_label("Title").fill("New1")
    page.get_by_label("Content").fill("Test1")
    page.get_by_role("button", name="Preview").click()
    page.get_by_role("button", name="Back to edit").click()
    page.get_by_role("button", name="Save").click()
    page.goto("/blog/list")
    expect(page.locator("body")).to_contain_text("New1")
