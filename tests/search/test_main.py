import pytest
from playwright.sync_api import Page, expect

from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AnyExtractedModel,
    ExtractedActivity,
    ExtractedPrimarySource,
    ExtractedResource,
)
from tests.conftest import build_pagination_regex, build_ui_label_regex


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_index(
    frontend_url: str, writer_user_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = writer_user_page

    # load page and establish section is visible
    page.goto(frontend_url)
    section = page.get_by_test_id("search-results-section")
    expect(section).to_be_visible()
    page.screenshot(path="tests_search_test_main-test_index-on-load.png")

    # check heading is showing
    expect(page.get_by_test_id("search-results-summary")).to_be_visible()

    # check mex primary source is showing
    primary_source = page.get_by_test_id(
        f"result-{MEX_PRIMARY_SOURCE_STABLE_TARGET_ID}"
    )
    expect(primary_source.first).to_be_visible()

    # check activity is showing
    activity = page.get_by_test_id(f"result-{extracted_activity.stableTargetId}")
    activity.scroll_into_view_if_needed()
    expect(activity).to_be_visible()
    expect(activity).to_contain_text("info@contact-point.one")  # resolved preview

    page.screenshot(path="tests_search_test_main-test_index-focus-activity.png")


@pytest.mark.integration
@pytest.mark.usefixtures("load_pagination_dummy_data")
def test_pagination(
    frontend_url: str,
    writer_user_page: Page,
) -> None:
    page = writer_user_page
    page.goto(frontend_url)

    pagination_previous = page.get_by_test_id("pagination-previous-button")
    pagination_next = page.get_by_test_id("pagination-next-button")
    pagination_page_select = page.get_by_test_id("pagination-page-select")

    pagination_page_select.scroll_into_view_if_needed()
    page.screenshot(path="tests_search_test_main_test_pagination.png")

    # check if:
    # - previous is disabled
    # - select shows all expected page numbers
    # - next is enabled
    expect(pagination_previous).to_be_disabled()
    expect(pagination_page_select).to_have_text("1")
    pagination_page_select.click()
    opt1 = page.get_by_role("option", name="1")
    expect(opt1).to_be_visible()
    expect(opt1).to_have_attribute("data-state", "checked")
    expect(page.get_by_role("option", name="2")).to_be_visible()
    expect(page.get_by_role("option", name="3")).to_be_visible()
    expect(pagination_next).to_be_enabled()
    # close the overlay, otherwise u cant click sth else
    opt1.click()

    pagination_next.click()
    expect(pagination_previous).to_be_enabled()
    expect(pagination_page_select).to_have_text("2")
    expect(pagination_next).to_be_enabled()

    pagination_next.click()
    expect(pagination_previous).to_be_enabled()
    expect(pagination_page_select).to_have_text("3")
    expect(pagination_next).to_be_disabled()


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
    search_input = page.get_by_test_id("search-input")
    expect(search_input).to_be_visible()
    search_input.fill("mex")
    search_input.press("Enter")
    expect(page.get_by_text(build_pagination_regex(1, 1))).to_be_visible()
    page.screenshot(
        path="tests_search_test_main-test_search_input-on-search-input-1-found.png"
    )

    search_input.fill("totally random search dPhGDHu3uiEcU6VNNs0UA74bBdubC3")
    page.get_by_test_id("search-button").click()
    expect(page.get_by_text(build_pagination_regex(0, 0))).to_be_visible()
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
    expect(page.get_by_text(build_pagination_regex(1, 1))).to_be_visible()
    page.screenshot(
        path="tests_search_test_main-test_entity_types-on-select-entity-1-found.png"
    )
    entity_types.get_by_text("Activity").click()


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_had_primary_sources(
    frontend_url: str,
    writer_user_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    page = writer_user_page
    page.goto(frontend_url)

    extracted_primary_source_one = dummy_data_by_identifier_in_primary_source["ps-1"]
    assert isinstance(extracted_primary_source_one, ExtractedPrimarySource)

    # check sidebar is showing
    sidebar = page.get_by_test_id("search-sidebar")
    expect(sidebar).to_be_visible()

    # activate tab for had primary source filtering
    tab = page.get_by_test_id("reference-filter-strategy-had-primary-source-tab")
    tab.click()

    # check primary sources are showing and functioning
    primary_sources = page.get_by_test_id("had-primary-sources")
    primary_sources.scroll_into_view_if_needed()
    expect(primary_sources).to_be_visible()
    # check that title is resolved if primary source has a title
    assert (
        extracted_primary_source_one.title[0].value
        in primary_sources.all_text_contents()[0]
    )

    primary_sources.get_by_text("Primary Source One").click()
    summary = page.get_by_test_id("search-results-summary")
    expect(summary).to_be_visible()
    expect(summary).to_contain_text(build_pagination_regex(4, 4))
    page.screenshot(
        path="tests_search_test_main-test_had_primary_sources-on-select-primary-source-1-found.png"
    )
    primary_sources.get_by_text("Primary Source One").click()


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_load_search_params(
    frontend_url: str,
    writer_user_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    page = writer_user_page
    expected_model = dummy_data_by_identifier_in_primary_source["cp-2"]
    page.goto(
        f"{frontend_url}/?q=help&page=1&entityType=ContactPoint&entityType=Consent"
        f"&hadPrimarySource={expected_model.hadPrimarySource}&referenceFilterStrategy=had_primary_source"
    )

    # check 1 item is showing
    expect(page.get_by_text(build_pagination_regex(1, 1))).to_be_visible()
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
def test_reference_filter_fields_for_entity_type(
    frontend_url: str,
    writer_user_page: Page,
) -> None:
    page = writer_user_page
    page.goto(frontend_url)
    page.wait_for_selector("[data-testid='page-body']")

    hps_tab = page.get_by_test_id("reference-filter-strategy-had-primary-source-tab")
    hps_tab.click()
    expect(page.get_by_test_id("had-primary-sources")).to_be_visible()

    dyn_tab = page.get_by_test_id("reference-filter-strategy-dynamic-tab")
    dyn_tab.click()
    expect(page.get_by_test_id("reference-field-filter")).to_be_visible()

    # select person entity
    entity_types = page.get_by_test_id("entity-types")
    entity_types.get_by_text("Person").click()

    reference_field_filter = page.get_by_test_id("reference-field-filter")
    ref_filter_field = reference_field_filter.get_by_test_id(
        "reference-field-filter-field"
    )
    ref_filter_field.click()

    page.screenshot(
        path="tests_search_test_main-test_reference_filter_fields_for_entity_type-on_field_click.png"
    )

    expected_person_fields = [
        "Fachgebiet",
        "Affiliation",
        "Primärsystem",
        "Stabiler Identifikator",
    ]
    for field in expected_person_fields:
        select_item = page.get_by_role("option", name=field, exact=True)
        expect(select_item).to_be_visible()


@pytest.mark.parametrize(
    ("locale_id", "expected_items"),
    [
        pytest.param(
            "de-DE",
            [
                "Affiliation",
                "Autor*in",
                "Datei",
                "Fachgebiet",
                "Kontakt",
                "Nachfolge von",
            ],
            id="de-DE",
        ),
        pytest.param(
            "en-US",
            [
                "Affiliation",
                "Access platform",
                "Contact",
                "Author",
                "Files",
                "Publisher",
            ],
            id="en-US",
        ),
    ],
)
@pytest.mark.integration
def test_reference_filter_field_translation(
    frontend_url: str, writer_user_page: Page, locale_id: str, expected_items: list[str]
) -> None:
    page = writer_user_page
    page.goto(frontend_url)
    page.wait_for_selector("[data-testid='page-body']")

    # switch language to specifid locale
    lang_switcher = page.get_by_test_id("language-switcher")
    lang_switcher.click()
    page.get_by_test_id(f"language-switcher-menu-item-{locale_id}").click()

    # check expected items existing
    page.get_by_test_id("reference-field-filter-field").click()
    for item in expected_items:
        expect(page.get_by_role("option", name=item, exact=True)).to_be_visible()


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_reference_filter(
    frontend_url: str,
    writer_user_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    page = writer_user_page
    page.goto(frontend_url)

    contact = dummy_data_by_identifier_in_primary_source["cp-1"]

    # open select
    page.get_by_test_id("reference-field-filter-field").click()
    # click concat option
    page.get_by_role("option", name="Kontakt").click()
    # add invalid field
    page.get_by_test_id("reference-field-filter-add-id").click()
    page.get_by_test_id("reference-field-filter-id-0").fill("invalidIdentifier!")
    # check for validation error msg
    expect(
        page.get_by_test_id("reference-field-filter").get_by_text("pattern")
    ).to_be_visible()
    page.screenshot(
        path="tests_search_test_main-test_reference_filter-reference_filter_invalid_search.png"
    )

    # set correct contact identifier
    page.get_by_test_id("reference-field-filter-id-0").fill(contact.stableTargetId)
    expect(
        page.get_by_test_id("reference-field-filter").get_by_text("pattern")
    ).not_to_be_visible()

    page.screenshot(
        path="tests_search_test_main-test_reference_filter-reference_filter_valid_search.png"
    )
    expect(page.get_by_text(build_pagination_regex(3, 3))).to_be_visible()


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_push_search_params(
    frontend_url: str,
    writer_user_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    page = writer_user_page
    primary_source = dummy_data_by_identifier_in_primary_source["ps-1"]
    assert type(primary_source) is ExtractedPrimarySource

    # load page and verify url
    page.goto(frontend_url)
    page.wait_for_url("**/")

    # select an entity type
    entity_types = page.get_by_test_id("entity-types")
    expect(entity_types).to_be_visible()
    page.screenshot(path="tests_search_test_main-test_push_search_params-on-load.png")
    entity_types.get_by_text("Activity").click()
    checked = entity_types.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(1)
    page.screenshot(path="tests_search_test_main-test_push_search_params-on-click.png")

    # expect parameter change to be reflected in url
    page.wait_for_url("**/?page=1&entityType=Activity&referenceFilterStrategy=dynamic")

    # add a query string to the search constraints
    search_input = page.get_by_test_id("search-input")
    expect(search_input).to_be_visible()
    search_input.fill("Une activité active")
    search_input.press("Enter")

    # expect parameter change to be reflected in url
    page.wait_for_url(
        "**/?q=Une+activit%C3%A9+active&page=1&entityType=Activity"
        "&referenceFilterStrategy=dynamic"
    )

    # activate tab for had primary source filtering
    tab = page.get_by_test_id("reference-filter-strategy-had-primary-source-tab")
    tab.click()

    # select a primary source
    primary_sources = page.get_by_test_id("had-primary-sources")
    expect(primary_sources).to_be_visible()
    page.screenshot(path="tests_search_test_main-test_push_search_params-on-load-2.png")
    checkbox = primary_sources.get_by_text(primary_source.title[0].value)
    expect(checkbox).to_be_visible()
    checkbox.click()
    page.screenshot(
        path="tests_search_test_main-test_push_search_params-on-click-2.png"
    )
    expect(page.get_by_test_id("search-results-section")).to_be_visible()
    checked = primary_sources.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(1)

    # expect parameter change to be reflected in url
    page.wait_for_url(
        "**/?q=Une+activit%C3%A9+active&page=1&entityType=Activity"
        "&referenceFilterStrategy=had_primary_source"
        f"&hadPrimarySource={primary_source.stableTargetId}"
    )


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_additional_titles_badge(
    frontend_url: str,
    writer_user_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    # search for resources
    page = writer_user_page
    page.goto(f"{frontend_url}/?entityType=Resource")

    resource_r2 = dummy_data_by_identifier_in_primary_source["r-2"]
    assert isinstance(resource_r2, ExtractedResource)
    resource_r2_result = page.get_by_test_id(f"result-{resource_r2.stableTargetId}")
    first_title = resource_r2.title[0]

    # expect title is visible and there are additional titles for 'r2'
    expect(resource_r2_result).to_contain_text(first_title.value)
    addi_title_badge = resource_r2_result.get_by_test_id("additional-titles-badge")
    expect(addi_title_badge).to_have_text(
        build_ui_label_regex("components.titles.additional_titles")
    )

    # hover additional titles
    box = addi_title_badge.bounding_box()
    assert box
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    addi_title_badge.hover()
    page.screenshot(path="tests_search_test_additional_titles_badge_hover.png")

    # check tooltip content
    tooltip = page.get_by_test_id("tooltip-additional-titles")
    expect(tooltip).to_be_visible()
    expect(tooltip).not_to_contain_text(first_title.value)
    for title in resource_r2.title[1:]:
        expect(tooltip).to_contain_text(title.value)
