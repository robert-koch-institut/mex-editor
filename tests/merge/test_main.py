import pytest
from playwright.sync_api import Page, expect

from mex.common.models import (
    AnyExtractedModel,
    ExtractedContactPoint,
    ExtractedResource,
)
from tests.conftest import build_pagination_regex, build_ui_label_regex


@pytest.fixture
def merge_page(
    frontend_url: str,
    writer_user_page: Page,
) -> Page:
    page = writer_user_page
    page.goto(f"{frontend_url}/merge")
    page_body = page.get_by_test_id("page-body")
    expect(page_body).to_be_visible()
    page.screenshot(path="tests_merge_items_test_main-test_index-on-load.png")
    return page


@pytest.mark.integration
def test_index(merge_page: Page) -> None:
    page = merge_page

    # load page and establish both section headings are visible
    section = page.get_by_test_id("create-heading-merged")
    expect(section).to_be_visible()
    section = page.get_by_test_id("create-heading-extracted")
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
    expect(page.get_by_text(build_pagination_regex(1, 1))).to_be_visible()
    page.screenshot(
        path="tests_merge_items_test_main-test_merged_search_input-on-search-input-1-found.png"
    )

    # check merged clear button is working
    page.get_by_test_id("clear-button-merged").click()
    checked = entity_types_merged.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(0)
    assert page.get_by_test_id("search-input-merged").input_value() == ""
    page.screenshot(
        path="tests_merge_items_test_main-test_merged_search_input-clear-input.png"
    )

    # check search trigger by entity type
    entity_types_merged.get_by_text("ContactPoint").click()
    expect(page.get_by_text(build_pagination_regex(2, 2))).to_be_visible()


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
    expect(page.get_by_text(build_pagination_regex(1, 1))).to_be_visible()
    page.screenshot(
        path="tests_merge_items_test_main-test_extracted_search_input-on-search-input-1-found.png"
    )

    # check extracted clear button is working
    page.get_by_test_id("clear-button-extracted").click()
    checked = entity_types_extracted.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(0)
    assert page.get_by_test_id("search-input-extracted").input_value() == ""
    page.screenshot(
        path="tests_merge_items_test_main-test_extracted_search_input-clear-input.png"
    )

    # check search trigger by entity type
    entity_types_extracted.get_by_text("ContactPoint").click()
    expect(page.get_by_text(build_pagination_regex(2, 2))).to_be_visible()


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_select_result_extracted(
    merge_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    page = merge_page

    # check extracted search result selection is working
    search_input_extracted = page.get_by_test_id("search-input-extracted")
    expect(search_input_extracted).to_be_visible()
    search_input_extracted.fill("contact")
    entity_types_extracted = page.get_by_test_id("entity-types-extracted")
    expect(entity_types_extracted).to_be_visible()
    entity_types_extracted.get_by_text("ContactPoint").click()
    page.get_by_test_id("search-button-extracted").click()
    expect(page.get_by_text(build_pagination_regex(2, 2))).to_be_visible()
    contact_point_1 = dummy_data_by_identifier_in_primary_source["cp-1"]
    result = page.get_by_test_id(f"result-extracted-{contact_point_1.identifier}")
    result.get_by_role("checkbox").click()
    checked = entity_types_extracted.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(1)
    page.screenshot(
        path="tests_merge_items_test_main-test_select_result_extracted-select.png"
    )


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_select_result_merged(
    merge_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    page = merge_page

    # check merged search result selection is working
    search_input_merged = page.get_by_test_id("search-input-merged")
    expect(search_input_merged).to_be_visible()
    search_input_merged.fill("contact")
    entity_types_merged = page.get_by_test_id("entity-types-merged")
    expect(entity_types_merged).to_be_visible()
    entity_types_merged.get_by_text("ContactPoint").click()
    page.get_by_test_id("search-button-merged").click()
    expect(page.get_by_text(build_pagination_regex(2, 2))).to_be_visible()
    contact_point_1 = dummy_data_by_identifier_in_primary_source["cp-1"]
    result = page.get_by_test_id(f"result-merged-{contact_point_1.stableTargetId}")
    result.get_by_role("checkbox").click()
    checked = entity_types_merged.get_by_role("checkbox", checked=True)
    expect(checked).to_have_count(1)
    page.screenshot(
        path="tests_merge_items_test_main-test_select_result_merged-select.png"
    )


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_resolves_identifier(
    merge_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    page = merge_page
    contact_point_1 = dummy_data_by_identifier_in_primary_source["cp-1"]
    assert isinstance(contact_point_1, ExtractedContactPoint)
    activity_1 = dummy_data_by_identifier_in_primary_source["a-1"]

    entity_types_extracted = page.get_by_test_id("entity-types-extracted")
    expect(entity_types_extracted).to_be_visible()
    entity_types_extracted.get_by_text("Activity").click()
    page.get_by_test_id("search-button-extracted").click()
    expect(
        page.get_by_test_id("extracted-results-summary").get_by_text(
            build_pagination_regex(1, 1)
        )
    ).to_be_visible()
    page.screenshot(path="tests_merge_test_main-test_resolves_identifier.png")
    result = page.get_by_test_id(f"result-extracted-{activity_1.identifier}")
    email = result.get_by_text(f"{contact_point_1.email[0]}")
    expect(email).to_be_visible()


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_additional_titles_badge(
    merge_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    # search for resources
    page = merge_page
    a = page.get_by_test_id("entity-types-extracted")
    a.get_by_role("checkbox", name="Resource", exact=True).click()

    resource_r2 = dummy_data_by_identifier_in_primary_source["r-2"]
    assert isinstance(resource_r2, ExtractedResource)
    resource_r2_result = page.get_by_test_id(
        f"result-extracted-{resource_r2.identifier}"
    )
    expect(resource_r2_result).to_be_visible()
    page.screenshot(path="tests_merge_test_additional_titles_badge_on_load.png")
    first_title = resource_r2.title[0]

    # expect title is visible and there are additional titles for 'r2'
    expect(resource_r2_result).to_contain_text(first_title.value)
    additional_title_badge = page.get_by_test_id("additional-titles-badge").first
    expect(additional_title_badge).to_be_visible()
    page.screenshot(path="tests_merge_test_additional_titles_badge_on_visible.png")
    expect(additional_title_badge).to_have_text(
        build_ui_label_regex("components.titles.additional_titles")
    )

    # hover additional titles
    box = additional_title_badge.bounding_box()
    assert box
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    additional_title_badge.hover()
    page.screenshot(path="tests_merge_test_additional_titles_badge_on_hover.png")

    # check tooltip content
    tooltip = page.get_by_test_id("tooltip-additional-titles")
    expect(tooltip).to_be_visible()
    expect(tooltip).not_to_contain_text(first_title.value)
    for title in resource_r2.title[1:]:
        expect(tooltip).to_contain_text(title.value)
