import re

import pytest
from playwright.sync_api import Page, expect

from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.ingest.models import ALL_AUX_PROVIDERS, AuxProvider
from tests.test_utils import build_pagination_regex


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
            "UNKOWNBLABLABLA",
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
            "UNKOWNBLABLABLA",
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
    result = connector.fetch_extracted_items(entity_type=[f"Extracted{stem_type}"])
    assert result.total == 0
    items_before = result.total

    # go to the correct tab
    aux_provider_tab = page.get_by_role("tab", name=aux_provider)
    expect(aux_provider_tab).to_be_enabled(timeout=30000)
    aux_provider_tab.click()
    search_input = page.get_by_test_id("search-input")
    expect(search_input).to_be_visible()
    expect(search_input).to_be_enabled()

    # trigger invalid search
    search_input.fill(invalid_search)
    search_input.press("Enter")
    expect(search_input).to_be_enabled(timeout=30000)
    page.screenshot(
        path=f"tests_ingest_test_main-roundtrip_{aux_provider}-invalid-search.png"
    )

    # test no results are found
    results_summary = page.get_by_test_id("search-results-summary")
    expect(results_summary).to_be_visible()
    expect(results_summary).to_contain_text(build_pagination_regex(0, 0))

    # trigger valid search
    search_input.fill(valid_search)
    search_input.press("Enter")
    expect(search_input).to_be_enabled(timeout=30000)
    page.screenshot(
        path=f"tests_ingest_test_main-roundtrip_{aux_provider}-valid-search.png"
    )

    # test pagination is showing
    prev_button = page.get_by_test_id("pagination-previous-button")
    expect(prev_button).to_be_disabled(timeout=30000)
    expect(page.get_by_test_id("pagination-next-button")).to_be_visible()
    expect(page.get_by_test_id("pagination-page-select")).to_be_visible()

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
        path=f"tests_ingest_test_main-roundtrip_{aux_provider}-ingested.png"
    )
    page.reload()
    expect(ingest_button).to_be_disabled()
    page.screenshot(
        path=f"tests_ingest_test_main-roundtrip_{aux_provider}-ingested-reload.png"
    )

    # count the items afterwards
    result = connector.fetch_extracted_items(entity_type=[f"Extracted{stem_type}"])
    assert result.total > items_before


@pytest.mark.integration
def test_infobox_visibility_and_content(ingest_page: Page) -> None:
    expected_callout_content: dict[AuxProvider, re.Pattern] = {
        AuxProvider.LDAP: re.compile(r"\w+"),
        AuxProvider.WIKIDATA: re.compile(r"\w+"),
    }

    page = ingest_page

    for provider in ALL_AUX_PROVIDERS:
        tab = page.get_by_role("tab", name=provider)
        tab.click(
            timeout=50000
        )  # high timeout cuz tab might be disabled due to loading

        tab_content = page.locator(f"[id*='{provider}'][role='tabpanel']")
        callout = tab_content.locator(".rt-CalloutRoot")

        expected_content = expected_callout_content.get(provider)
        if expected_content:
            expect(callout).to_have_count(1)
            expect(callout).to_have_text(expected_content)
        else:
            expect(callout).to_have_count(0)

        page.screenshot(path=f"tests_ingest_test_main-test_infobox_{provider}.png")
