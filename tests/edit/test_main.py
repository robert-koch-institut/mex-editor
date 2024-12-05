import re
from typing import cast

import pytest
from playwright.sync_api import Page, expect

from mex.common.models import AnyExtractedModel, ExtractedActivity


@pytest.fixture
def extracted_activity(load_dummy_data: list[AnyExtractedModel]) -> ExtractedActivity:
    return cast(ExtractedActivity, load_dummy_data[-1])


@pytest.fixture
def edit_page(
    frontend_url: str, writer_user_page: Page, extracted_activity: ExtractedActivity
) -> Page:
    page = writer_user_page
    page.goto(f"{frontend_url}/item/{extracted_activity.stableTargetId}")
    section = page.get_by_test_id("edit-section")
    expect(section).to_be_visible()
    return page


@pytest.mark.integration
def test_edit_nav_bar(edit_page: Page) -> None:
    page = edit_page
    nav_bar = page.get_by_test_id("nav-bar")
    page.screenshot(path="tests_edit_test_main-test_edit_nav_bar.png")
    expect(nav_bar).to_be_visible()
    nav_item = nav_bar.get_by_text("Edit", exact=True)
    expect(nav_item).to_have_class(re.compile("rt-underline-always"))


@pytest.mark.integration
def test_edit_heading(edit_page: Page) -> None:
    page = edit_page
    heading = page.get_by_test_id("edit-heading")
    page.screenshot(path="tests_edit_test_main-test_edit_heading.png")
    expect(heading).to_be_visible()
    assert re.match(r"Aktivität 1\s*de", heading.inner_text())


@pytest.mark.integration
def test_edit_fields(edit_page: Page, extracted_activity: ExtractedActivity) -> None:
    page = edit_page
    identifier_in_primary_source = page.get_by_test_id(
        "field-identifierInPrimarySource-name"
    )
    page.screenshot(path="tests_edit_test_main-test_edit_fields.png")
    expect(identifier_in_primary_source).to_be_visible()
    all_fields = page.get_by_role("row").all()
    assert len(all_fields) == len(extracted_activity.model_fields)


@pytest.mark.integration
def test_edit_primary_sources(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    had_primary_source = page.get_by_test_id(
        "primary-source-hadPrimarySource-gGdOIbDIHRt35He616Fv5q"
    )
    page.screenshot(path="tests_edit_test_main-test_edit_primary_sources.png")
    expect(had_primary_source).to_be_visible()
    all_primary_sources = page.get_by_text(extracted_activity.hadPrimarySource).all()
    set_values = extracted_activity.model_dump(exclude_none=True, exclude_defaults=True)
    assert len(all_primary_sources) == len(set_values)


@pytest.mark.integration
def test_edit_text(edit_page: Page) -> None:
    page = edit_page
    text = page.get_by_test_id("value-title-gGdOIbDIHRt35He616Fv5q_0")
    page.screenshot(path="tests_edit_test_main-test_edit_text.png")
    expect(text).to_be_visible()
    expect(text).to_contain_text("Aktivität 1")  # text value
    expect(text).to_contain_text("de")  # language badge


@pytest.mark.integration
def test_edit_vocab(edit_page: Page) -> None:
    page = edit_page
    theme = page.get_by_test_id("value-theme-gGdOIbDIHRt35He616Fv5q_0")
    page.screenshot(path="tests_edit_test_main-test_edit_vocab.png")
    expect(theme).to_be_visible()
    expect(theme).to_contain_text("INFECTIOUS_DISEASES_AND_EPIDEMIOLOGY")  # theme value
    expect(theme).to_contain_text("Theme")  # vocabulary name


@pytest.mark.integration
def test_edit_link(edit_page: Page) -> None:
    page = edit_page
    website = page.get_by_test_id("value-website-gGdOIbDIHRt35He616Fv5q_0")
    page.screenshot(path="tests_edit_test_main-test_edit_link.png")
    expect(website).to_be_visible()
    link = website.get_by_role("link")
    expect(link).to_contain_text("Activity Homepage")  # link title
    expect(link).to_have_attribute("href", "https://activity-1")  # link href
    expect(link).to_have_attribute("target", "_blank")  # external link


@pytest.mark.integration
def test_edit_temporal(edit_page: Page) -> None:
    page = edit_page
    start = page.get_by_test_id("value-start-gGdOIbDIHRt35He616Fv5q_0")
    page.screenshot(path="tests_edit_test_main-test_edit_temporal.png")
    expect(start).to_be_visible()
    expect(start).to_contain_text("24. Dezember 1999")  # temporal localization


@pytest.mark.integration
def test_edit_identifier(edit_page: Page) -> None:
    page = edit_page
    contact = page.get_by_test_id("value-contact-gGdOIbDIHRt35He616Fv5q_2")
    page.screenshot(path="tests_edit_test_main-test_edit_identifier.png")
    expect(contact).to_be_visible()
    link = contact.get_by_role("link")
    expect(link).to_contain_text("cWWm02l1c6cucKjIhkFqY4")  # not resolved yet
    expect(link).to_have_attribute("href", "/item/cWWm02l1c6cucKjIhkFqY4/")  # link href
    expect(link).not_to_have_attribute("target", "_blank")  # internal link
