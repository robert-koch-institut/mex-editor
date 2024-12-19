import re
from typing import cast

import pytest
from playwright.sync_api import Page, expect

from mex.common.fields import MERGEABLE_FIELDS_BY_CLASS_NAME
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
    funding_program = page.get_by_test_id("field-fundingProgram-name")
    page.screenshot(path="tests_edit_test_main-test_edit_fields.png")
    expect(funding_program).to_be_visible()
    all_fields = page.get_by_role("row").all()
    assert len(all_fields) == len(
        MERGEABLE_FIELDS_BY_CLASS_NAME[extracted_activity.entityType]
    )


@pytest.mark.integration
def test_edit_primary_sources(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    primary_source = page.get_by_test_id(
        f"primary-source-title-{extracted_activity.hadPrimarySource}-name"
    )
    page.screenshot(path="tests_edit_test_main-test_edit_primary_sources.png")
    expect(primary_source).to_be_visible()
    expect(primary_source).to_contain_text(extracted_activity.hadPrimarySource)
    link = primary_source.get_by_role("link")
    expect(link).to_have_attribute(
        "href", f"/item/{extracted_activity.hadPrimarySource}/"
    )


@pytest.mark.integration
def test_edit_text(edit_page: Page, extracted_activity: ExtractedActivity) -> None:
    page = edit_page
    text = page.get_by_test_id(f"value-title-{extracted_activity.hadPrimarySource}-0")
    page.screenshot(path="tests_edit_test_main-test_edit_text.png")
    expect(text).to_be_visible()
    expect(text).to_contain_text("Aktivität 1")  # text value
    expect(text).to_contain_text("de")  # language badge


@pytest.mark.integration
def test_edit_vocab(edit_page: Page, extracted_activity: ExtractedActivity) -> None:
    page = edit_page
    theme = page.get_by_test_id(f"value-theme-{extracted_activity.hadPrimarySource}-0")
    page.screenshot(path="tests_edit_test_main-test_edit_vocab.png")
    expect(theme).to_be_visible()
    expect(theme).to_contain_text("INFECTIOUS_DISEASES_AND_EPIDEMIOLOGY")  # theme value
    expect(theme).to_contain_text("Theme")  # vocabulary name


@pytest.mark.integration
def test_edit_link(edit_page: Page, extracted_activity: ExtractedActivity) -> None:
    page = edit_page
    website = page.get_by_test_id(
        f"value-website-{extracted_activity.hadPrimarySource}-0"
    )
    page.screenshot(path="tests_edit_test_main-test_edit_link.png")
    expect(website).to_be_visible()
    link = website.get_by_role("link")
    expect(link).to_contain_text("Activity Homepage")  # link title
    expect(link).to_have_attribute("href", "https://activity-1")  # link href
    expect(link).to_have_attribute("target", "_blank")  # external link


@pytest.mark.integration
def test_edit_temporal(edit_page: Page, extracted_activity: ExtractedActivity) -> None:
    page = edit_page
    start = page.get_by_test_id(f"value-start-{extracted_activity.hadPrimarySource}-0")
    page.screenshot(path="tests_edit_test_main-test_edit_temporal.png")
    expect(start).to_be_visible()
    expect(start).to_contain_text("24. Dezember 1999")  # temporal localization


@pytest.mark.integration
def test_edit_identifier(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    contact = page.get_by_test_id(
        f"value-contact-{extracted_activity.hadPrimarySource}-2"
    )
    page.screenshot(path="tests_edit_test_main-test_edit_identifier.png")
    expect(contact).to_be_visible()
    link = contact.get_by_role("link")
    expect(link).to_contain_text(extracted_activity.contact[2])  # not resolved yet
    expect(link).to_have_attribute(
        "href",
        f"/item/{extracted_activity.contact[2]}/",  # link href
    )
    expect(link).not_to_have_attribute("target", "_blank")  # internal link
