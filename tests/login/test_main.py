import logging
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from pydantic import SecretStr


@pytest.mark.integration
def test_login(page: Page, writer_user_credentials: tuple[str, SecretStr]) -> None:
    page.goto("http://localhost:3000")
    page.get_by_placeholder("Username").fill(
        writer_user_credentials[0],
    )
    page.get_by_placeholder("Password").fill(
        writer_user_credentials[1].get_secret_value(),
    )
    page.screenshot(path="test_login-login-screen.jpeg")
    assert Path("test_login-login-screen.jpeg").exists()
    logging.info(Path("test_login-login-screen.jpeg").as_posix())

    page.get_by_text("Log in").click()
    expect(page.get_by_test_id("search-container")).to_be_visible()
    page.screenshot(path="test_login-redirected-home.jpeg")
    assert Path("test_login-redirected-home.jpeg").exists()
    logging.info(Path("test_login-redirected-home.jpeg").as_posix())
