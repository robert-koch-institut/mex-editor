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
    section = page.get_by_test_id("search-section")
    expect(section).to_be_visible()
    page.screenshot(path="tests_search_test_main-test_index-on-load.jpeg")

    # check heading is showing
    heading = page.get_by_test_id("search-heading")
    expect(heading).to_be_visible()
    assert heading.inner_text() == "Search"

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
