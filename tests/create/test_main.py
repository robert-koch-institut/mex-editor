import re

import pytest
from playwright.sync_api import Page, expect

from mex.common.fields import MERGEABLE_FIELDS_BY_CLASS_NAME
from mex.common.models import (
    ExtractedActivity,
)


@pytest.fixture
def create_page(
    frontend_url: str,
    writer_user_page: Page,
) -> Page:
    page = writer_user_page
    page.goto(f"{frontend_url}/create")
    page_body = page.get_by_test_id("page-body")
    expect(page_body).to_be_visible()
    return page


@pytest.mark.integration
def test_create_page_updates_nav_bar(create_page: Page) -> None:
    page = create_page
    nav_bar = page.get_by_test_id("nav-bar")
    page.screenshot(path="tests_create_test_main-test_create_page_updates_nav_bar.png")
    expect(nav_bar).to_be_visible()
    nav_item = nav_bar.locator(".nav-item").all()[1]
    expect(nav_item).to_contain_text("Create")
    expect(nav_item).to_have_class(re.compile("rt-underline-always"))


@pytest.mark.integration
def test_v_renders_heading(create_page: Page) -> None:
    page = create_page
    heading = page.get_by_test_id("create-heading")
    page.screenshot(path="tests_create_test_main-test_create_page_renders_heading.png")
    expect(heading).to_be_visible()


@pytest.mark.integration
def test_create_page_renders_fields(
    create_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = create_page
    funding_program = page.get_by_test_id("field-fundingProgram-name")
    page.screenshot(path="tests_create_test_main-test_create_page_renders_fields.png")
    expect(funding_program).to_be_visible()
    all_fields = page.get_by_role("row").all()
    assert len(all_fields) == len(
        MERGEABLE_FIELDS_BY_CLASS_NAME[extracted_activity.entityType]
    )
