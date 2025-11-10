import pytest
from playwright.sync_api import Page, expect
from pydantic import SecretStr


@pytest.mark.integration
def test_login(
    frontend_url: str, page: Page, writer_user_credentials: tuple[str, SecretStr]
) -> None:
    page.goto(f"{frontend_url}/")

    page.get_by_test_id("input-username").fill(
        writer_user_credentials[0],
    )
    page.get_by_test_id("input-password").fill(
        writer_user_credentials[1].get_secret_value(),
    )
    page.screenshot(path="tests_login_test_main-test_login-on-load.png")

    page.get_by_test_id("login-button").click()
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    expect(page.get_by_test_id("search-results-section")).to_be_visible()
    page.screenshot(path="tests_login_test_main-test_login-after-login.png")

    page.get_by_test_id("user-menu").click()
    expect(page.get_by_test_id("logout-button")).to_be_visible()
    page.get_by_test_id("logout-button").click()
    expect(page.get_by_test_id("login-button")).to_be_visible()


@pytest.mark.integration
def test_login_with_enter_key(
    frontend_url: str, page: Page, writer_user_credentials: tuple[str, SecretStr]
) -> None:
    page.goto(f"{frontend_url}/")

    page.get_by_test_id("input-username").fill(writer_user_credentials[0])
    password_input = page.get_by_test_id("input-password")
    password_input.fill(writer_user_credentials[1].get_secret_value())
    page.screenshot(path="tests_login_test_main-test_login_with_enter_key-on-load.png")

    password_input.press("Enter")
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    expect(page.get_by_test_id("search-results-section")).to_be_visible()
    page.screenshot(
        path="tests_login_test_main-test_login_with_enter_key-after-login.png"
    )
