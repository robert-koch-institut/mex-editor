import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def consent_page(
    frontend_url: str,
    writer_user_page: Page,
) -> Page:
    page = writer_user_page
    page.goto(f"{frontend_url}/consent")
    page_body = page.get_by_test_id("page-body")
    expect(page_body).to_be_visible()
    page.screenshot(path="tests_consent_test_main-test_index-on-load.png")
    return page


@pytest.mark.integration
def test_index(consent_page: Page) -> None:
    page = consent_page

    # load page and check user information is visible
    user_data = page.get_by_test_id("user-data")
    expect(user_data).to_be_visible()

    # check resource and project sections are visible
    resources_section = page.get_by_test_id("user-resources")
    expect(resources_section).to_be_visible()
    projects_section = page.get_by_test_id("user-projects")
    expect(projects_section).to_be_visible()

    # check consent box and buttons are visible
    consent_box = page.get_by_test_id("consent-box")
    expect(consent_box).to_be_visible()
