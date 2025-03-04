import re

import pytest
from playwright.sync_api import Page, expect

from mex.common.models import AnyExtractedModel


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_index(frontend_url: str, writer_user_page: Page) -> None:
    page = writer_user_page

    # load page and establish section is visible
    page.goto(frontend_url)
    section = page.get_by_test_id("search-results-section")
    expect(section).to_be_visible()
    page.screenshot(path="tests_search_test_main-test_index-on-load.png")

    # check heading is showing
    expect(page.get_by_text("Showing 7 of 7 items")).to_be_visible()

    # check mex primary source is showing
    primary_source = page.get_by_text(re.compile(r"^PrimarySource$"))
    expect(primary_source.first).to_be_visible()

    # check activity is showing
    activity = page.get_by_text(
        re.compile(r"Aktivität 1\s*de\s*A1.*1999-12-24\s*day\s*2023-01-01")
    )
    activity.scroll_into_view_if_needed()
    expect(activity).to_be_visible()
    page.screenshot(path="tests_search_test_main-test_index-focus-activity.png")


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_pagination(
    frontend_url: str,
    writer_user_page: Page,
) -> None:
    page = writer_user_page
    page.goto(frontend_url)

    # check sidebar is showing and disabled and selector is on page 1
    pagination_previous = page.get_by_test_id("pagination-previous-button")
    pagination_next = page.get_by_test_id("pagination-next-button")
    pagination_page_select = page.get_by_test_id("pagination-page-select")
    expect(pagination_previous).to_be_disabled()
    expect(pagination_next).to_be_disabled()
    assert pagination_page_select.inner_text() == "1"


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_search_input(
    frontend_url: str,
    writer_user_page: Page,
) -> None:
    page = writer_user_page
    page.goto(frontend_url)

    # check sidebar is showing
    sidebar = page.get_by_test_id("search-sidebar")
    expect(sidebar).to_be_visible()

    # test search input is showing and functioning
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()
    search_input.fill("mex")
    expect(page.get_by_text("Showing 1 of 1 items")).to_be_visible()
    page.screenshot(
        path="tests_search_test_main-test_search_input-on-search-input-1-found.png"
    )

    search_input.fill("totally random search dPhGDHu3uiEcU6VNNs0UA74bBdubC3")
    expect(page.get_by_text("Showing 0 of 0 items")).to_be_visible()
    page.screenshot(
        path="tests_search_test_main-test_search_input-on-search-input-0-found.png"
    )
    search_input.fill("")


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_entity_types(
    frontend_url: str,
    writer_user_page: Page,
) -> None:
    page = writer_user_page
    page.goto(frontend_url)

    # check sidebar is showing
    sidebar = page.get_by_test_id("search-sidebar")
    expect(sidebar).to_be_visible()

    # check entity types are showing and functioning
    entity_types = page.get_by_test_id("entity-types")
    expect(entity_types).to_be_visible()
    assert "PrimarySource" in entity_types.all_text_contents()[0]

    entity_types.get_by_text("Activity").click()
    expect(page.get_by_text("Showing 1 of 1 items")).to_be_visible()
    page.screenshot(
        path="tests_search_test_main-test_entity_types-on-select-entity-1-found.png"
    )
    entity_types.get_by_text("Activity").click()


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_had_primary_sources(
    frontend_url: str,
    writer_user_page: Page,
) -> None:
    page = writer_user_page
    page.goto(frontend_url)

    # check sidebar is showing
    sidebar = page.get_by_test_id("search-sidebar")
    expect(sidebar).to_be_visible()

    # check entity types are showing and functioning
    primary_sources = page.get_by_test_id("had-primary-sources")
    expect(primary_sources).to_be_visible()
    assert "00000000000000" in primary_sources.all_text_contents()[0]

    primary_sources.get_by_text("00000000000000").click()
    expect(page.get_by_text("Showing 3 of 3 items")).to_be_visible()
    page.screenshot(
        path="tests_search_test_main-test_had_primary_sources-on-select-primary-source-1-found.png"
    )
    primary_sources.get_by_text("00000000000000").click()


@pytest.mark.integration
def test_load_search_params(
    frontend_url: str,
    writer_user_page: Page,
    load_dummy_data: list[AnyExtractedModel],
) -> None:
    page = writer_user_page
    expected_model, *_ = [
        m for m in load_dummy_data if m.identifierInPrimarySource == "cp-2"
    ]
    page.goto(
        f"{frontend_url}/?q=help&page=1&entityType=ContactPoint&entityType=Consent"
        f"&hadPrimarySource={expected_model.hadPrimarySource}"
    )

    # check 1 item is showing
    expect(page.get_by_text("Showing 1 of 1 items")).to_be_visible()
    page.screenshot(
        path="tests_search_test_main-test_load_search_params-on-params-loaded.png"
    )
    search_result_cards = page.locator(".search-result-card")
    expect(search_result_cards).to_have_count(1)
    expect(search_result_cards).to_contain_text("help@contact-point.two")

    # check entity types are loaded from url
    entity_types = page.get_by_test_id("entity-types")
    unchecked = entity_types.get_by_role("checkbox", checked=False)
    expect(unchecked).to_have_count(11)
    checked = entity_types.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(2)

    # check primary sources are loaded from url
    primary_sources = page.get_by_test_id("had-primary-sources")
    unchecked = primary_sources.get_by_role("checkbox", checked=False)
    expect(unchecked).to_have_count(2)
    checked = primary_sources.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(1)


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_push_search_params(
    frontend_url: str,
    writer_user_page: Page,
) -> None:
    page = writer_user_page

    # load page and verify url
    page.goto(frontend_url)
    page.wait_for_url("**/", timeout=10)

    # select an entity type
    entity_types = page.get_by_test_id("entity-types")
    expect(entity_types).to_be_visible()
    page.screenshot(path="tests_search_test_main-test_push_search_params-on-load.png")
    entity_types.get_by_text("Activity").click()
    checked = entity_types.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(1)
    page.screenshot(path="tests_search_test_main-test_push_search_params-on-click.png")

    # expect parameter change to be reflected in url
    page.wait_for_url("**/?page=1&entityType=Activity")

    # add a query string to the search constraints
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()
    search_input.fill("Can I search here?")

    # expect parameter change to be reflected in url
    page.wait_for_url("**/?q=Can+I+search+here%3F&page=1&entityType=Activity")

    # select a primary source
    primary_sources = page.get_by_test_id("had-primary-sources")
    expect(primary_sources).to_be_visible()
    page.screenshot(path="tests_search_test_main-test_push_search_params-on-load-2.png")
    primary_sources.get_by_text("00000000000000").click()
    checked = primary_sources.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(1)
    page.screenshot(
        path="tests_search_test_main-test_push_search_params-on-click-2.png"
    )

    # expect parameter change to be reflected in url
    page.wait_for_url(
        "**/?q=Can+I+search+here%3F&page=1&entityType=Activity&hadPrimarySource=00000000000000"
    )
