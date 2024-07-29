import pytest
from playwright.sync_api import Page, expect
from pydantic import SecretStr


@pytest.mark.integration()
def test_login(page: Page, writer_user_credentials: tuple[str, SecretStr]) -> None:
    page.goto("http://localhost:3000")

    page.get_by_placeholder("Username").fill(
        writer_user_credentials[0],
    )
    page.get_by_placeholder("Password").fill(
        writer_user_credentials[1].get_secret_value(),
    )
    page.screenshot(path="tests_login_test_main-test_login-on-load.jpeg")

    page.get_by_text("Log in").click()
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    page.screenshot(path="tests_login_test_main-test_login-after-login.jpeg")
