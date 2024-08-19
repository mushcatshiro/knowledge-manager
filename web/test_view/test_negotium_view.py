import pytest

from playwright.sync_api import Page, expect

from .commons import clear_session, setup_auth_session


@pytest.fixture(scope="function")
def create_negs(context, page: Page, new_context):
    """
    playwright's fixture only supports function and session scopes.
    bypass the limitation by using testing all workflows in one function.

    payload creates a root neg and 3 children negs, one expired, one completed
    , one with priority 1 and one with priority 2
    """
    payload = [
        {"Title": "test1", "Content": "test1"},
        {
            "Title": "test2",
            "Content": "test2",
            "Deadline": "2022-01-01 00:00:00",
            "Parent Id": "1",
        },  # expired
        {"Title": "test3", "Content": "test3", "Priority": "1", "Parent Id": "1"},
        {
            "Title": "test4",
            "Content": "test4",
            "Priority": "2",
            "Completed": True,
            "Parent Id": "1",
        },
        {"Title": "test5", "Content": "test5", "Priority": "2", "Parent Id": "1"},
    ]
    setup_auth_session(page)

    for p in payload:
        page.goto("/negotium/create")
        page.get_by_label("Title").fill(p["Title"])
        page.get_by_label("Content").fill(p["Content"])
        if "Deadline" in p:
            page.get_by_placeholder("YYYY-MM-DD HH:MM:SS").fill(p["Deadline"])
        if "Priority" in p:
            page.get_by_label("Priority").select_option(p["Priority"])
        if "Completed" in p:
            page.get_by_label("Completed").check()
        if "Parent Id" in p:
            page.get_by_label("Parent Id").fill(p["Parent Id"])
        page.get_by_role("button", name="Submit").click()
    yield payload
    clear_session(page)


def test_not_logged_in(page: Page):
    page.goto("/negotium")  # with or without trailing slash?
    expect(page.locator("body")).to_contain_text("Unauthorized access: 401")
    page.goto("/negotium/chain/1")
    expect(page.locator("body")).to_contain_text("Unauthorized access: 401")
    page.goto("/negotium/get/1")
    expect(page.locator("body")).to_contain_text("Unauthorized access: 401")
    page.goto("/negotium/edit/1")
    expect(page.locator("body")).to_contain_text("Unauthorized access: 401")
    page.goto("/negotium/create")  # with or without trailing slash?
    expect(page.locator("body")).to_contain_text("Unauthorized access: 401")
    page.goto("/negotium/create/1")
    expect(page.locator("body")).to_contain_text("Unauthorized access: 401")


def test_negotium_workflow(page: Page, create_negs):
    """
    - create new negs
    - update negs (including pid, completed, priority, context and title)
    - check priority matrix
    - check chains, root negs counts
    """
    page.goto("/negotium")
    expect(page.locator("body")).to_contain_text("test1")  # root neg
    # priority matrix; BUG can be better
    expect(page.locator("body")).to_contain_text("0 2")
    expect(page.locator("body")).to_contain_text("1 1")
    expect(page.locator("body")).to_contain_text("2 1")
    # root negs
    expect(page.locator("body")).to_contain_text("test1 test1 Negotium chain")

    # create new negs
    page.goto("/negotium/create")
    page.get_by_label("Title").fill("test6")  # new root neg
    page.get_by_label("Content").fill("test6")
    page.get_by_role("button", name="Submit").click()

    page.goto("/negotium/create")
    page.get_by_label("Title").fill("test7")  # child of new root neg
    page.get_by_label("Content").fill("test7")
    page.get_by_label("Parent Id").fill("6")
    page.get_by_role("button", name="Submit").click()

    page.goto("/negotium")
    expect(page.locator("body")).to_contain_text("0 4")
    expect(page.locator("body")).to_contain_text(
        "test6 test6 Negotium chain"
    )  # root neg

    # update negs
    # update priority
    page.goto("/negotium/edit/7")
    page.get_by_label("Priority").select_option("1")
    page.get_by_role("button", name="Submit").click()
    page.goto("/negotium")
    expect(page.locator("body")).to_contain_text("0 3")
    expect(page.locator("body")).to_contain_text("1 2")

    # update completed
    page.goto("/negotium/edit/7")
    page.get_by_label("Completed").check()
    page.get_by_role("button", name="Submit").click()
    page.goto("/negotium")
    expect(page.locator("body")).to_contain_text("1 1")

    # update context
    page.goto("/negotium/edit/7")
    page.get_by_label("Content").fill("test7 updated")
    page.get_by_role("button", name="Submit").click()
    page.goto("/negotium/get/7")
    expect(page.locator("body")).to_contain_text("test7 updated")

    # update title
    page.goto("/negotium/edit/6")
    page.get_by_label("Title").fill("test6 updated title")
    page.get_by_role("button", name="Submit").click()
    page.goto("/negotium/get/6")
    expect(page.locator("xpath=/html/body/div/form/div[2]/input")).to_have_attribute(
        "value", "test6 updated title"
    )

    # update pid to root neg 1, check at neg chain
    page.goto("/negotium/chain/1")
    expect(page.locator("body")).not_to_contain_text("test7")
    page.goto("/negotium/edit/7")
    page.get_by_label("Parent Id").fill("1")
    page.get_by_role("button", name="Submit").click()
    page.goto("/negotium/chain/1")
    expect(page.locator("body")).to_contain_text("test7")

    # neg chain check expired red; completed green;
    expect(page.locator("xpath=.//div[contains(@class, 'card')][2]")).to_have_class(
        "card text-white bg-danger"
    )
    expect(page.locator("xpath=.//div[contains(@class, 'card')][6]")).to_have_class(
        "card text-white bg-success"
    )
