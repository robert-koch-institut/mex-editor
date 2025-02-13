import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def aux_page(frontend_url: str, writer_user_page: Page) -> Page:
    page = writer_user_page
    page.goto(f"{frontend_url}/aux-import")
    section = page.get_by_test_id("aux-nav-bar")
    expect(section).to_be_visible()
    return page


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_aux_navbar(aux_page: Page) -> None:
    page = aux_page
    nav_bar = page.get_by_test_id("aux-nav-bar")
    page.screenshot(path="tests_aux_search_test_main-test_aux_navbar.png")
    expect(nav_bar).to_be_visible()
    nav_item = nav_bar.get_by_text("Wikidata")
    expect(nav_item).to_be_visible()


@pytest.mark.integration
@pytest.mark.external
def test_search_results(aux_page: Page) -> None:
    page = aux_page
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()

    # test search input is showing correctly
    search_input.fill("this doesn't exist gs871s9j91kksWN0shx345jnj")
    expect(page.get_by_text("showing 0 of total 0 items found")).to_be_visible()
    page.screenshot(path="tests_aux_search_test_main-test_search-input-0-found.png")

    # test expand button works
    search_input.fill("rki")
    expand_all_properties_button = page.get_by_test_id("expand-properties-button").nth(
        1
    )
    expect(page.get_by_test_id("all-properties-display")).not_to_be_visible()
    expand_all_properties_button.click()
    expect(page.get_by_test_id("all-properties-display")).to_be_visible()
    page.screenshot(path="tests_aux_search_test_main-test_expand_button.png")


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_pagination(aux_page: Page) -> None:
    page = aux_page

    # test pagination is showing and properly disabled
    pagination_previous = page.get_by_test_id("pagination-previous-button")
    pagination_next = page.get_by_test_id("pagination-next-button")
    pagination_page_select = page.get_by_test_id("pagination-page-select")
    expect(pagination_previous).to_be_disabled()
    expect(pagination_next).to_be_disabled()
    assert pagination_page_select.inner_text() == ""
