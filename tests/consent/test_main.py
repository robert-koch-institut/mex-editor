from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Page, expect

from mex.editor.settings import EditorSettings


@pytest.fixture
def login_ldap_user(
    page: Page,
    frontend_url: str,
) -> Page:
    settings = EditorSettings.get()
    url = urlsplit(settings.ldap_url.get_secret_value())
    page.goto(f"{frontend_url}/consent")
    page.get_by_placeholder("Username").fill(url.username)  # type:ignore [arg-type]
    page.get_by_placeholder("Password").fill(url.password)  # type:ignore [arg-type]
    page.get_by_test_id("login-button").click()
    page.wait_for_timeout(3000)
    page.screenshot(path="tests_ldap_login.png")
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    return page


@pytest.fixture
def consent_page(
    frontend_url: str,
    login_ldap_user: Page,
) -> Page:
    page = login_ldap_user
    page.goto(f"{frontend_url}/consent")
    page_body = page.get_by_test_id("page-body")
    expect(page_body).to_be_visible()
    page.screenshot(path="tests_consent_test_main-test_index-on-load.png")
    return page


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_projects_and_resources(consent_page: Page) -> None:
    page = consent_page
    resources_section = page.get_by_test_id("user-resources")
    expect(resources_section).to_be_visible()
    expect(resources_section).to_contain_text("Bioinformatics Resource 1")
    projects_section = page.get_by_test_id("user-projects")
    expect(projects_section).to_be_visible()
    expect(projects_section).to_contain_text("Aktivität 1")


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_index(consent_page: Page) -> None:
    page = consent_page

    # load page and check user information is visible
    user_data = page.get_by_test_id("user-data")
    expect(user_data).to_be_visible()
    expect(user_data).to_contain_text("Bernd")
    expect(user_data).to_contain_text("person_1@example.com")

    # check consent box and buttons are visible
    consent_box = page.get_by_test_id("consent-box")
    expect(consent_box).to_be_visible()


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_submit_consent(consent_page: Page) -> None:
    page = consent_page

    # check if given consent is submitted
    page.get_by_role("button", name="Einwilligen").click()
    consent_status = page.get_by_test_id("consent-status")
    consent_status.scroll_into_view_if_needed()
    page.screenshot(path="tests_consent_test_main-test_submit_consent_valid.png")
    toast = page.locator(".editor-toast").first
    expect(toast).to_be_visible()
    expect(toast).to_contain_text("Consent was saved successfully.")
    expect(consent_status).to_contain_text("VALID_FOR_PROCESSING")

    # check if denied consent is submitted
    page.get_by_role("button", name="Ablehnen").click()
    page.screenshot(path="tests_consent_test_main-test_submit_consent_invalid.png")
    toast = page.locator(".editor-toast").first
    expect(toast).to_be_visible()
    expect(toast).to_contain_text("Consent was saved successfully.")
    expect(consent_status).to_contain_text("INVALID_FOR_PROCESSING")
