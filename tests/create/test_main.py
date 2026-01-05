import re

import pytest
from playwright.sync_api import Page, expect

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.fields import MERGEABLE_FIELDS_BY_CLASS_NAME
from mex.common.models import AnyExtractedModel


@pytest.fixture
def create_page(
    frontend_url: str,
    writer_user_page: Page,
    load_dummy_data: None,  # noqa: ARG001
) -> Page:
    page = writer_user_page
    page.goto(f"{frontend_url}/create")
    page_body = page.get_by_test_id("page-body")
    expect(page_body).to_be_visible()
    return page


@pytest.mark.integration
def test_create_page_updates_nav_bar(create_page: Page) -> None:
    page = create_page
    nav_bar = page.get_by_test_id("nav-bar")
    page.screenshot(path="tests_create_test_main-test_create_page_updates_nav_bar.png")
    expect(nav_bar).to_be_visible()
    nav_item = nav_bar.locator(".nav-item").all()[1]
    expect(nav_item).to_contain_text("Create")
    expect(nav_item).to_have_class(re.compile("rt-underline-always"))


@pytest.mark.integration
def test_create_page_renders_heading(create_page: Page) -> None:
    page = create_page
    heading = page.get_by_test_id("create-heading")
    page.screenshot(path="tests_create_test_main-test_create_page_renders_heading.png")
    expect(heading).to_be_visible()


@pytest.mark.integration
def test_create_page_renders_fields(create_page: Page) -> None:
    page = create_page
    page.get_by_test_id("entity-type-select").click()
    page.get_by_role("option", name="Resource", exact=True).click()
    page.screenshot(
        path="tests_create_test_main-test_create_page_renders_fields_select.png"
    )
    expect(page.get_by_role("row")).to_have_count(
        len(MERGEABLE_FIELDS_BY_CLASS_NAME["ExtractedResource"])
    )


@pytest.mark.integration
def test_create_page_test_additive_buttons(create_page: Page) -> None:
    page = create_page
    new_additive_button = page.get_by_test_id("new-additive-description-00000000000000")
    new_additive_button.scroll_into_view_if_needed()
    page.screenshot(
        path="tests_create_test_main-test_edit_page_renders_new_additive_button.png"
    )
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()

    additive_rule_input = page.get_by_test_id("additive-rule-description-0-text")
    expect(additive_rule_input).to_be_visible()

    remove_additive_rule_button = page.get_by_test_id(
        "additive-rule-description-0-remove-button"
    )
    expect(remove_additive_rule_button).to_be_visible()
    remove_additive_rule_button.click()
    expect(remove_additive_rule_button).not_to_be_visible()


@pytest.mark.requires_rki_infrastructure
@pytest.mark.integration
def test_create_page_submit_item(create_page: Page) -> None:
    page = create_page
    new_additive_button = page.get_by_test_id("new-additive-title-00000000000000")
    new_additive_button.scroll_into_view_if_needed()
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()

    additive_rule_input = page.get_by_test_id("additive-rule-title-0-text")
    expect(additive_rule_input).to_be_visible()
    additive_rule_input.fill("Test01234567")
    page.screenshot(path="tests_create_test_main-test_edit_page_save_item_input.png")

    submit_button = page.get_by_test_id("submit-button")
    submit_button.click()
    expect(page.get_by_text("AccessPlatform was saved successfully")).to_be_visible()
    connector = BackendApiConnector.get()
    result = connector.fetch_merged_items(query_string="Test01234567")
    assert result.total == 1


@pytest.mark.parametrize(
    (
        "locale_id",
        "expected_access_platform_field_label",
    ),
    [
        pytest.param("de-DE", "Zugriffsplattform", id="locale de-DE"),
        pytest.param("en-US", "Access platform", id="locale en-US"),
    ],
)
@pytest.mark.integration
def test_language_switcher(
    create_page: Page, locale_id: str, expected_access_platform_field_label: str
) -> None:
    # language switcher should be there
    lang_switcher = create_page.get_by_test_id("language-switcher")
    expect(lang_switcher).to_be_visible()

    # change language and wait for reload
    lang_switcher.click()
    create_page.get_by_test_id(f"language-switcher-menu-item-{locale_id}").click()

    # select entity_type resource
    create_page.get_by_test_id("entity-type-select").click(timeout=30_000)
    create_page.get_by_role("option", name="Resource", exact=True).click()
    create_page.wait_for_timeout(20000)

    # find the accessPlatform field label and check the text
    field_access_platform = create_page.get_by_test_id("field-accessPlatform-name")
    expect(field_access_platform).to_have_text(expected_access_platform_field_label)


@pytest.mark.integration
def test_search_reference_dialog(
    create_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    dialog_prefix = "search-reference-dialog"
    field_contact = create_page.get_by_test_id("field-contact")
    field_contact.get_by_test_id("new-additive-contact-00000000000000").click()
    field_contact.get_by_test_id(f"{dialog_prefix}-button").click()

    query_input = create_page.get_by_test_id(f"{dialog_prefix}-query-input")
    search_results = create_page.get_by_test_id(f"{dialog_prefix}-search-results")
    expect(search_results.locator(".search-result-card")).to_have_count(3)

    query_input.fill("OU")
    query_input.press("Enter")
    expect(search_results.locator(".search-result-card")).to_have_count(1)

    ou = dummy_data_by_identifier_in_primary_source["ou-1"]
    create_page.get_by_test_id(f"{dialog_prefix}-result-select-button").click()
    expect(
        create_page.get_by_test_id(f"{dialog_prefix}-query-input")
    ).not_to_be_visible()
    expect(
        field_contact.get_by_test_id("additive-rule-contact-0-identifier")
    ).to_have_value(ou.stableTargetId)

    field_uic = create_page.get_by_test_id("field-unitInCharge")
    field_uic.get_by_test_id("new-additive-unitInCharge-00000000000000").click()
    field_uic.get_by_test_id(f"{dialog_prefix}-button").click()
    expect(search_results.locator(".search-result-card")).to_have_count(1)
    create_page.locator(".rt-DialogOverlay").click(position={"x": 10, "y": 10})
    expect(
        field_uic.get_by_test_id("additive-rule-unitInCharge-0-identifier")
    ).to_have_value("")
