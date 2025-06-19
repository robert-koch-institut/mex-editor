import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def merge_page(
    frontend_url: str,
    writer_user_page: Page,
) -> Page:
    page = writer_user_page
    page.goto(f"{frontend_url}/merge-items")
    page_body = page.get_by_test_id("page-body")
    expect(page_body).to_be_visible()
    page.screenshot(path="tests_merge_items_test_main-test_index-on-load.png")
    return page


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_index(merge_page: Page) -> None:
    page = merge_page

    # load page and establish both section headings are visible
    section = page.get_by_test_id("search-merged")
    expect(section).to_be_visible()
    section = page.get_by_test_id("search-extracted")
    expect(section).to_be_visible()

    # check submit button is showing
    expect(page.get_by_test_id("submit-button")).to_be_visible()


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_search_input_merged(merge_page: Page) -> None:
    page = merge_page

    # check merged search input is showing and working
    search_input_merged = page.get_by_test_id("search-input-merged")
    expect(search_input_merged).to_be_visible()
    search_input_merged.fill("Unit 1")
    entity_types_merged = page.get_by_test_id("entity-types-merged")
    expect(entity_types_merged).to_be_visible()
    entity_types_merged.get_by_text("OrganizationalUnit").click()
    checked = entity_types_merged.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(1)
    page.get_by_test_id("search-button-merged").click()
    expect(page.get_by_text("Showing 1 of 1 items")).to_be_visible()
    page.screenshot(
        path="tests_merge_items_test_main-test_merged_search_input-on-search-input-1-found.png"
    )

    # check merged clear button is working
    page.get_by_test_id("clear-button-merged").click()
    checked = entity_types_merged.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(0)
    search_merged = page.get_by_test_id("search-merged")
    expect(search_merged.get_by_text("Showing 0 of 0 items")).to_be_visible()
    page.screenshot(
        path="tests_merge_items_test_main-test_merged_search_input-clear-input.png"
    )

    # test merged search input with no results
    search_input_merged.fill("totally random search dPhGDHu3uiEcU6VNNs0UA74bBdubC3")
    page.get_by_test_id("search-button-merged").click()
    expect(page.get_by_text("Showing 0 of 0 items")).to_be_visible()
    page.screenshot(
        path="tests_merge_items_test_main-test_merged_search_input-on-search-input-0-found.png"
    )


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_search_input_extracted(merge_page: Page) -> None:
    page = merge_page

    # check extracted search input is showing and working
    search_input_extracted = page.get_by_test_id("search-input-extracted")
    expect(search_input_extracted).to_be_visible()
    search_input_extracted.fill("Unit 1")
    entity_types_extracted = page.get_by_test_id("entity-types-extracted")
    expect(entity_types_extracted).to_be_visible()
    entity_types_extracted.get_by_text("OrganizationalUnit").click()
    checked = entity_types_extracted.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(1)
    page.get_by_test_id("search-button-extracted").click()
    expect(page.get_by_text("Showing 1 of 1 items")).to_be_visible()
    page.screenshot(
        path="tests_merge_items_test_main-test_extracted_search_input-on-search-input-1-found.png"
    )

    # check extracted clear button is working
    page.get_by_test_id("clear-button-extracted").click()
    checked = entity_types_extracted.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(0)
    extracted_search = page.get_by_test_id("search-extracted")
    expect(extracted_search.get_by_text("Showing 0 of 0 items")).to_be_visible()
    page.screenshot(
        path="tests_merge_items_test_main-test_extracted_search_input-clear-input.png"
    )

    # test extracted search input with no results
    search_input_extracted.fill("totally random search dPhGDHu3uiEcU6VNNs0UA74bBdubC3")
    page.get_by_test_id("search-button-extracted").click()
    expect(page.get_by_text("Showing 0 of 0 items")).to_be_visible()
    page.screenshot(
        path="tests_merge_items_test_main-test_extracted_search_input-on-search-input-0-found.png"
    )


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_select_result_extracted(merge_page: Page) -> None:
    page = merge_page

    # check extracted search result selection is working
    search_input_extracted = page.get_by_test_id("search-input-extracted")
    expect(search_input_extracted).to_be_visible()
    search_input_extracted.fill("contact")
    entity_types_extracted = page.get_by_test_id("entity-types-extracted")
    expect(entity_types_extracted).to_be_visible()
    entity_types_extracted.get_by_text("ContactPoint").click()
    page.get_by_test_id("search-button-extracted").click()
    expect(page.get_by_text("Showing 2 of 2 items")).to_be_visible()
    page.get_by_test_id("result-extracted-0").get_by_role("checkbox").click()
    checked = entity_types_extracted.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(1)
    page.screenshot(
        path="tests_merge_items_test_main-test_select_result_extracted-select.png"
    )


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_select_result_merged(merge_page: Page) -> None:
    page = merge_page

    # check merged search result selection is working
    search_input_merged = page.get_by_test_id("search-input-merged")
    expect(search_input_merged).to_be_visible()
    search_input_merged.fill("contact")
    entity_types_merged = page.get_by_test_id("entity-types-merged")
    expect(entity_types_merged).to_be_visible()
    entity_types_merged.get_by_text("ContactPoint").click()
    page.get_by_test_id("search-button-merged").click()
    expect(page.get_by_text("Showing 2 of 2 items")).to_be_visible()
    page.get_by_test_id("result-merged-0").get_by_role("checkbox").click()
    checked = entity_types_merged.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(1)
    page.screenshot(
        path="tests_merge_items_test_main-test_select_result_merged-select.png"
    )
