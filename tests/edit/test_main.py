import re

import pytest
from playwright.sync_api import Page, expect

from mex.common.models import AnyExtractedModel


@pytest.mark.integration
def test_index(
    writer_user_page: Page,
    load_dummy_data: list[AnyExtractedModel],
) -> None:
    extracted_activity = load_dummy_data[-1]
    page = writer_user_page

    # load page and establish section is visible
    page.goto(f"http://localhost:3000/item/{extracted_activity.stableTargetId}")
    section = page.get_by_test_id("edit-section")
    expect(section).to_be_visible()
    page.screenshot(path="tests_edit_test_main-test_index-on-load.jpeg")

    # check heading is showing
    heading = page.get_by_test_id("edit-heading")
    expect(heading).to_be_visible()
    assert heading.inner_text() == "Aktivität 1"

    # check nav item is selected
    nav_bar = page.get_by_test_id("nav-bar")
    expect(nav_bar).to_be_visible()
    nav_item = nav_bar.get_by_text("Edit", exact=True)
    expect(nav_item).to_have_class(re.compile("rt-underline-always"))

    # check title is showing
    title = section.get_by_test_id("edit-heading")
    expect(title).to_contain_text("Aktivität 1")

    # check shortName field card is showing
    field = section.get_by_text("shortName", exact=True)
    field.scroll_into_view_if_needed()
    page.screenshot(path="tests_edit_test_main-test_index-focus-field.jpeg")
    expect(field).to_be_visible()

    # check shortName value card is showing
    value = section.get_by_text("value: A1", exact=True)
    expect(value).to_be_visible()

    # check primary source cards are showing
    primary_sources = section.get_by_text(extracted_activity.hadPrimarySource).all()
    set_values = extracted_activity.model_dump(exclude_none=True, exclude_defaults=True)
    assert len(primary_sources) == len(set_values)
