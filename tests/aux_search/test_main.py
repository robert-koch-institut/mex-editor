import pytest
from playwright.sync_api import Page, expect

from mex.common.backend_api.connector import BackendApiConnector


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


@pytest.mark.integration
@pytest.mark.external
def test_wikidata_search_and_import_results(aux_page: Page) -> None:
    page = aux_page
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()

    # test search input is showing correctly
    search_input.fill("this doesn't exist gs871s9j91kksWN0shx345jnj")
    search_input.press("Enter")
    page.screenshot(path="tests_aux_search_test_main-test_search-input-0-found.png")
    expect(page.get_by_text("showing 0 of")).to_be_visible()

    # test expand button works
    search_input.fill("Q12345")
    search_input.press("Enter")
    expand_all_properties_button = page.get_by_test_id("expand-properties-button").nth(
        1
    )
    page.screenshot(path="tests_aux_search_test_main-search_result.png")
    expect(page.get_by_text("Count von Count")).to_be_visible()
    expect(page.get_by_test_id("all-properties-display")).not_to_be_visible()
    expand_all_properties_button.click()
    expect(page.get_by_test_id("all-properties-display")).to_be_visible()
    page.screenshot(path="tests_aux_search_test_main-test_expand_button.png")

    # test import button works
    import_button = page.get_by_text("Import").nth(1)
    import_button.click()
    expect(page.get_by_text("Aux search result imported successfully")).to_be_visible()
    expect(import_button).to_be_disabled()
    page.screenshot(path="tests_aux_search_test_main-test_import_button.png")

    # test node was ingested into backend
    connector = BackendApiConnector.get()
    result = connector.fetch_extracted_items(q="Count von Count")
    assert result["total"] >= 1


@pytest.mark.integration
@pytest.mark.external
def test_ldap_search_and_import_results(aux_page: Page) -> None:
    page = aux_page
    ldap_tab = page.get_by_role("tab", name="LDAP")
    ldap_tab.click()
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()

    # test search input is showing correctly
    search_input.fill("doesn't exist gs871s9j91k*")
    search_input.press("Enter")
    expect(page.get_by_text("Showing 0 of")).to_be_visible()
    page.screenshot(
        path="tests_aux_search_test_main-test_ldap_search-input-0-found.png"
    )

    # test expand button works
    search_input.fill("Ciftci*")
    search_input.press("Enter")
    expand_all_properties_button = page.get_by_test_id("expand-properties-button").nth(
        1
    )
    page.screenshot(path="tests_aux_search_test_main-search_result_lap.png")
    expect(page.get_by_text("Ciftci, Zehra")).to_be_visible()
    expect(page.get_by_test_id("all-properties-display")).not_to_be_visible()
    expand_all_properties_button.click()
    expect(page.get_by_test_id("all-properties-display")).to_be_visible()
    page.screenshot(path="tests_aux_search_test_main-test_ldap_expand_button.png")

    # test import button works
    import_button = page.get_by_text("Import").nth(1)
    import_button.click()
    expect(page.get_by_text("Aux search result imported successfully")).to_be_visible()
    expect(import_button).to_be_disabled()
    page.screenshot(path="tests_aux_search_test_main-test_ldap_import_button.png")

    # test node was ingested into backend
    connector = BackendApiConnector.get()
    result = connector.fetch_extracted_items(q="Ciftci")
    assert result["total"] >= 1


@pytest.mark.integration
@pytest.mark.external
def test_orcid_search_and_import_results(aux_page: Page) -> None:
    page = aux_page
    orcid_tab = page.get_by_role("tab", name="Orcid")
    orcid_tab.click()
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()

    # test search input is showing correctly
    search_input.fill("doesn't exist gs871s9j91k*")
    expect(page.get_by_text("Showing 0 of")).to_be_visible()
    page.screenshot(
        path="tests_aux_search_test_main-test_orcid_search-input-0-found.png"
    )

    # test expand button works
    search_input.fill("Kamran")
    expand_all_properties_button = page.get_by_test_id("expand-properties-button").nth(
        1
    )
    page.screenshot(path="tests_aux_search_test_main-search_result_orcid.png")
    expect(page.get_by_text("Kamran")).to_be_visible()
    expect(page.get_by_test_id("all-properties-display")).not_to_be_visible()
    expand_all_properties_button.click()
    expect(page.get_by_test_id("all-properties-display")).to_be_visible()
    page.screenshot(path="tests_aux_search_test_main-test_orcid_expand_button.png")

    # test import button works
    import_button = page.get_by_text("Import").nth(1)
    import_button.click()
    expect(page.get_by_text("Aux search result imported successfully")).to_be_visible()
    expect(import_button).to_be_disabled()
    page.screenshot(path="tests_aux_search_test_main-test_orcid_import_button.png")

    # test node was ingested into backend
    connector = BackendApiConnector.get()
    result = connector.fetch_extracted_items(q="Kamran")
    assert result["total"] >= 1


@pytest.mark.integration
def test_pagination(aux_page: Page) -> None:
    page = aux_page

    # test pagination is showing and properly disabled
    pagination_previous = page.get_by_test_id("pagination-previous-button")
    pagination_next = page.get_by_test_id("pagination-next-button")
    pagination_page_select = page.get_by_test_id("pagination-page-select")
    expect(pagination_previous).to_be_disabled()
    expect(pagination_next).to_be_disabled()
    assert pagination_page_select.inner_text() == ""
