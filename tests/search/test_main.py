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
    page.screenshot(path="tests_search_test_main-test_index-on-load.png")

    # check heading is showing
    expect(page.get_by_text("showing 7 of total 7 items found")).to_be_visible()

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
    page.screenshot(path="tests_search_test_main-test_index-focus-activity.png")


@pytest.mark.integration()
@pytest.mark.usefixtures("load_dummy_data")
def test_pagination(
    writer_user_page: Page,
) -> None:
    page = writer_user_page
    page.goto("http://localhost:3000")

    # check sidebar is showing and disabled and selector is on page 1
    pagination_previous = page.get_by_test_id("pagination-previous-button")
    pagination_next = page.get_by_test_id("pagination-next-button")
    pagination_page_select = page.get_by_test_id("pagination-page-select")
    expect(pagination_previous).to_be_disabled()
    expect(pagination_next).to_be_disabled()
    assert pagination_page_select.inner_text() == "1"


@pytest.mark.integration()
@pytest.mark.usefixtures("load_dummy_data")
def test_search_input(
    writer_user_page: Page,
) -> None:
    page = writer_user_page
    page.goto("http://localhost:3000")

    # check sidebar is showing
    sidebar = page.get_by_test_id("search-sidebar")
    expect(sidebar).to_be_visible()

    # test search input is showing and functioning
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()
    search_input.fill("mex")
    expect(page.get_by_text("showing 1 of total 1 items found")).to_be_visible()
    page.screenshot(
        path="tests_search_test_main-test_index-on-search-input-1-found.png"
    )

    search_input.fill("totally random search dPhGDHu3uiEcU6VNNs0UA74bBdubC3")
    expect(page.get_by_text("showing 0 of total 0 items found")).to_be_visible()
    page.screenshot(
        path="tests_search_test_main-test_index-on-search-input-0-found.png"
    )
    search_input.fill("")


@pytest.mark.integration()
@pytest.mark.usefixtures("load_dummy_data")
def test_entity_types(
    writer_user_page: Page,
) -> None:
    page = writer_user_page
    page.goto("http://localhost:3000")

    # check sidebar is showing
    sidebar = page.get_by_test_id("search-sidebar")
    expect(sidebar).to_be_visible()

    # check entity types are showing and functioning
    entity_types = page.get_by_test_id("entity-types")
    expect(entity_types).to_be_visible()
    assert (
        "MergedPrimarySource" and "MergedPerson" in entity_types.all_text_contents()[0]
    )
    entity_types.get_by_text("MergedActivity").click()
    expect(page.get_by_text("showing 1 of total 1 items found")).to_be_visible()
    page.screenshot(
        path="tests_search_test_main-test_index-on-select-entity-1-found.png"
    )
    entity_types.get_by_text("MergedActivity").click()
