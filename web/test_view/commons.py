import os

from playwright.sync_api import Page, expect


def setup_auth_session(page: Page):
    page.goto("/admin/login")
    page.locator("#token").fill(os.getenv("AUTH_TOKEN"))
    page.get_by_role("button", name="Login").click()


def clear_session(page: Page):
    page.goto("/admin/logout")
