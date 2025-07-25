import pytest
from playwright.sync_api import Page, expect

from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.ingest.models import ALL_AUX_PROVIDERS, AuxProvider


@pytest.fixture
def ingest_page(frontend_url: str, writer_user_page: Page) -> Page:
    page = writer_user_page
    page.goto(f"{frontend_url}/ingest")
    section = page.get_by_test_id("aux-tab-section")
    expect(section).to_be_visible()
    return page


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_aux_tab_section(ingest_page: Page) -> None:
    page = ingest_page
    nav_bar = page.get_by_test_id("aux-tab-section")
    page.screenshot(path="tests_ingest_test_main-test_aux_tab_section.png")
    expect(nav_bar).to_be_visible()


@pytest.mark.integration
@pytest.mark.external
def test_wikidata_search_and_ingest_results(ingest_page: Page) -> None:
    page = ingest_page
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()

    # test search input is showing correctly
    search_input.fill("Q000000")  # does not exist
    search_input.press("Enter")
    page.screenshot(path="tests_ingest_test_main-test_search-input-0-found.png")
    expect(page.get_by_text("showing 0 of")).to_be_visible()

    # test expand button works
    search_input.fill("Q12345")
    search_input.press("Enter")
    expand_all_properties_button = page.get_by_test_id("expand-properties-button").first
    page.screenshot(path="tests_ingest_test_main-search_result.png")
    expect(page.get_by_text("Count von Count")).to_be_visible()
    expect(page.get_by_test_id("all-properties-display")).not_to_be_visible()
    expand_all_properties_button.click()
    expect(page.get_by_test_id("all-properties-display")).to_be_visible()
    page.screenshot(path="tests_ingest_test_main-test_expand_button.png")

    # test ingest button works
    ingest_button = page.get_by_text("Ingest").first
    ingest_button.click()
    toast = page.locator(".editor-toast").first
    expect(toast).to_be_visible()
    expect(toast).to_contain_text("Organization was ingested successfully.")
    expect(ingest_button).to_be_disabled()
    page.screenshot(path="tests_ingest_test_main-test_ingest_button.png")

    # test node was ingested into backend
    connector = BackendApiConnector.get()
    result = connector.fetch_extracted_items("Count von Count", None, None, 0, 1)
    assert result.total >= 1


@pytest.mark.integration
@pytest.mark.external
def test_ldap_search_and_ingest_results(ingest_page: Page) -> None:
    # count the persons before
    connector = BackendApiConnector.get()
    result = connector.fetch_extracted_items(None, None, ["ExtractedPerson"], 0, 1)
    persons_before = result.total

    page = ingest_page
    ldap_tab = page.get_by_role("tab", name="LDAP")
    ldap_tab.click()
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()

    # test search input is showing correctly
    search_input.fill("doesn't exist gs871s9j91k*")
    search_input.press("Enter")
    page.screenshot(path="tests_ingest_test_main-test_ldap_search-input-0-found.png")
    expect(page.get_by_text("Showing 0 of")).to_be_visible()

    # test expand button works
    search_input.fill("L*")
    search_input.press("Enter")
    expand_all_properties_button = page.get_by_test_id("expand-properties-button").first
    page.screenshot(path="tests_ingest_test_main-search_result_lap.png")
    expect(page.get_by_test_id("all-properties-display")).not_to_be_visible()
    expand_all_properties_button.click()
    expect(page.get_by_test_id("all-properties-display")).to_be_visible()
    page.screenshot(path="tests_ingest_test_main-test_ldap_expand_button.png")

    # test ingest button works
    ingest_button = page.get_by_text("Ingest").first
    ingest_button.click()
    toast = page.locator(".editor-toast").first
    expect(toast).to_be_visible()
    expect(toast).to_contain_text("Person was ingested successfully.")
    expect(ingest_button).to_be_disabled()
    page.screenshot(path="tests_ingest_test_main-test_ldap_ingest_button.png")

    # count the persons after
    result = connector.fetch_extracted_items(None, None, ["ExtractedPerson"], 0, 1)
    assert result.total == persons_before + 1


@pytest.mark.integration
@pytest.mark.external
def test_orcid_search_and_ingest_results(ingest_page: Page) -> None:
    page = ingest_page
    orcid_tab = page.get_by_role("tab", name="Orcid")
    orcid_tab.click()
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()

    # test search input is showing correctly
    search_input.fill("doesn't exist gs871s9j91k*")
    page.screenshot(path="tests_ingest_test_main-test_orcid_search-input-0-found.png")
    expect(page.get_by_text("Showing 0 of")).to_be_visible()

    # test expand button works
    search_input.fill("Lars")
    page.screenshot(path="tests_ingest_test_main-search_result_orcid.png")
    expand_all_properties_button = page.get_by_test_id("expand-properties-button").nth(
        1
    )
    expect(page.get_by_text("Lars")).to_be_visible()
    expect(page.get_by_test_id("all-properties-display")).not_to_be_visible()
    expand_all_properties_button.click()
    expect(page.get_by_test_id("all-properties-display")).to_be_visible()
    page.screenshot(path="tests_ingest_test_main-test_orcid_expand_button.png")

    # test ingest button works
    ingest_button = page.get_by_text("Ingest").nth(1)
    ingest_button.click()
    expect(page.get_by_text("Person was ingested successfully")).to_be_visible()
    expect(ingest_button).to_be_disabled()
    page.screenshot(path="tests_ingest_test_main-test_orcid_ingest_button.png")

    # test node was ingested into backend
    connector = BackendApiConnector.get()
    result = connector.fetch_extracted_items("Lars", None, None, 0, 1)
    assert result.total >= 1


@pytest.mark.integration
def test_pagination(ingest_page: Page) -> None:
    page = ingest_page
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()
    search_input.fill("no such results")

    # test pagination is showing and properly disabled
    page.screenshot(path="tests_ingest_test_main-test_pagination.png")
    pagination_previous = page.get_by_test_id("pagination-previous-button")
    pagination_next = page.get_by_test_id("pagination-next-button")
    pagination_page_select = page.get_by_test_id("pagination-page-select")
    expect(pagination_previous).to_be_disabled()
    expect(pagination_next).to_be_disabled()
    assert pagination_page_select.inner_text() == ""


@pytest.mark.integration
def test_infobox_visibility_and_content(ingest_page: Page) -> None:
    expected_callout_content: dict[AuxProvider, str] = {
        AuxProvider.LDAP: 'Search users by their fullname. Please use "*" as placeholder e.g. "Muster*".',
        AuxProvider.WIKIDATA: 'Search Wikidata by "Concept URI". Please paste URI e.g. "http://www.wikidata.org/entity/Q918501".',
    }

    page = ingest_page

    for provider in ALL_AUX_PROVIDERS:
        tab = page.get_by_role("tab", name=provider)
        tab.click()

        tab_content = page.locator(f"[id*='{provider}'][role='tabpanel']")
        callout = tab_content.locator(".rt-CalloutRoot")

        expected_content = expected_callout_content.get(provider)
        if expected_content:
            expect(callout).to_have_count(1)
            expect(callout).to_have_text(expected_content)
        else:
            expect(callout).to_have_count(0)

        page.screenshot(
            path=f"tests_ingest_test_main-test_infobox_visibility_and_content_{provider}.png"
        )
