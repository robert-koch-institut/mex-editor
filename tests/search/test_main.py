import re

import pytest
from playwright.sync_api import Page, expect

from mex.common.models import AnyExtractedModel


@pytest.mark.integration()
def test_index(
    writer_user_page: Page,
    load_dummy_data: list[AnyExtractedModel],
) -> None:
    organizational_unit = load_dummy_data[-2]
    page = writer_user_page

    # load page and establish section is visible
    page.goto("http://localhost:3000")
    section = page.get_by_test_id("search-results-section")
    expect(section).to_be_visible()
    page.screenshot(path="tests_search_test_main-test_index-on-load.jpeg")

    # check heading is showing
    heading = page.get_by_test_id("search-results-heading")
    expect(heading).to_be_visible()
    assert heading.inner_text() == "showing 7 of total 7 items found"

    # check sidebar is showing
    sidebar = page.get_by_test_id("search-sidebar")
    expect(sidebar).to_be_visible()

    # check search input is showing
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()

    # check entity types are showing
    entity_types = page.get_by_test_id("entity-types")
    expect(entity_types).to_be_visible()
    assert (
        "MergedPrimarySource" and "MergedPerson" in entity_types.all_text_contents()[0]
    )

    # check pagination is showing
    pagination = page.get_by_test_id("pagination")
    expect(pagination).to_be_visible()
    assert "Previous" and "Next" in pagination.all_text_contents()[0]

    # check mex primary source is showing
    primary_source = page.get_by_text(
        re.compile(r"^MergedPrimarySource\s*00000000000000$")
    )
    expect(primary_source).to_be_visible()

    # check activity is showing
    activity = page.get_by_text(
        re.compile(
            r"^Aktivität 1\s*value: A1 . "
            + organizational_unit.stableTargetId  # unitInCharge
            + r" . 1999-12-24 . 2023-01-01$"
        )
    )
    activity.scroll_into_view_if_needed()
    expect(activity).to_be_visible()
    page.screenshot(path="tests_search_test_main-test_index-focus-activity.jpeg")
