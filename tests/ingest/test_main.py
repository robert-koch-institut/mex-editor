import pytest
from playwright.sync_api import Page, expect

from mex.common.backend_api.connector import BackendApiConnector


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


@pytest.mark.parametrize(
    ("aux_provider", "stem_type", "invalid_search", "valid_search"),
    [
        (
            "ldap",
            "Person",
            "doesn't exist gs871s9j91k*",
            "L*",
        ),
        (
            "wikidata",
            "Organization",
            "Q000000",
            "Q12345",
        ),
        (
            "orcid",
            "Person",
            "doesn't exist gs871s9j91k*",
            "Lars",
        ),
    ],
    ids=["ldap", "wikidata", "orcid"],
)
@pytest.mark.integration
@pytest.mark.external
def test_search_and_ingest_roundtrip(
    ingest_page: Page,
    aux_provider: str,
    stem_type: str,
    invalid_search: str,
    valid_search: str,
) -> None:
    page = ingest_page

    # count the items before
    connector = BackendApiConnector.get()
    result = connector.fetch_extracted_items(
        None, None, [f"Extracted{stem_type}"], 0, 1
    )
    items_before = result.total

    # go to the correct tab
    ldap_tab = page.get_by_role("tab", name=aux_provider)
    expect(ldap_tab).to_be_enabled(timeout=30000)
    ldap_tab.click()
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_visible()
    expect(search_input).to_be_enabled()

    # test search input is showing correctly
    search_input.fill(invalid_search)
    search_input.press("Enter")
    page.screenshot(
        path=f"tests_ingest_test_main-roundtrip_{aux_provider}-invalid-search.png"
    )
    expect(page.get_by_text("Showing 0 of")).to_be_visible()

    # trigger valid search
    search_input.fill(valid_search)
    search_input.press("Enter")
    page.screenshot(
        path=f"tests_ingest_test_main-roundtrip_{aux_provider}-valid-search.png"
    )
    expect(search_input).to_be_enabled()

    # test expand button works
    expand_button = page.get_by_test_id("expand-properties-button-0")
    expect(expand_button).to_be_visible()

    page.screenshot(path=f"tests_ingest_test_main-roundtrip_{aux_provider}.png")
    expect(page.get_by_test_id("all-properties-display")).not_to_be_visible()
    expand_button.click()
    expect(page.get_by_test_id("all-properties-display")).to_be_visible()
    page.screenshot(
        path=f"tests_ingest_test_main-roundtrip_{aux_provider}-expanded.png"
    )

    # test ingest button works
    ingest_button = page.get_by_test_id("ingest-button-0")
    ingest_button.click()
    toast = page.locator(".editor-toast").first
    expect(toast).to_be_visible()
    expect(toast).to_contain_text(f"{stem_type} was ingested successfully.")
    expect(ingest_button).to_be_disabled()
    page.screenshot(
        path=f"tests_ingest_test_main-roundtrip_{aux_provider}-imported.png"
    )

    # count the items afterwards
    result = connector.fetch_extracted_items(
        None, None, [f"Extracted{stem_type}"], 0, 1
    )
    assert result.total == items_before + 1


@pytest.mark.external
@pytest.mark.integration
def test_pagination_on_ldap_tab(ingest_page: Page) -> None:
    page = ingest_page
    search_input = page.get_by_placeholder("Search here...")
    expect(search_input).to_be_enabled()
    search_input.fill("no such results")

    # test pagination is showing and properly disabled
    pagination_previous = page.get_by_test_id("pagination-previous-button")
    pagination_next = page.get_by_test_id("pagination-next-button")
    pagination_page_select = page.get_by_test_id("pagination-page-select")
    page.screenshot(path="tests_ingest_test_main-test_pagination_on_ldap_tab.png")
    expect(pagination_previous).to_be_disabled()
    expect(pagination_next).to_be_disabled()
    expect(pagination_page_select).to_be_disabled()
