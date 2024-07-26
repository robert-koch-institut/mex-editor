import pytest
from playwright.sync_api import Page, expect

from mex.editor.settings import EditorSettings


@pytest.mark.integration
def test_login(page: Page) -> None:
    settings = EditorSettings.get()
    username, password = next(iter(settings.editor_user_database["write"].items()))

    page.goto("http://localhost:3000")
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill(password.get_secret_value())
    page.screenshot(path="test_login-login-screen.jpeg")

    page.get_by_text("Log in").click()
    expect(page.get_by_test_id("search-container")).to_be_visible()
    page.screenshot(path="test_login-redirected-home.jpeg")
