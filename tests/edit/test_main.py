import re

import pytest
from playwright.sync_api import Dialog, Page, expect

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.fields import MERGEABLE_FIELDS_BY_CLASS_NAME
from mex.common.models import (
    ActivityRuleSetRequest,
    AdditiveActivity,
    AnyExtractedModel,
    ExtractedActivity,
    ExtractedOrganizationalUnit,
    ExtractedPrimarySource,
    SubtractiveActivity,
)
from mex.common.transform import ensure_prefix
from mex.common.types import Identifier, Text, TextLanguage
from mex.editor.fields import REQUIRED_FIELDS_BY_CLASS_NAME
from mex.editor.rules.transform import get_required_mergeable_field_names


@pytest.fixture
def edit_page(
    frontend_url: str,
    writer_user_page: Page,
    extracted_activity: ExtractedActivity,
    load_dummy_data: None,  # noqa: ARG001
) -> Page:
    page = writer_user_page
    page.set_default_navigation_timeout(50000)
    page.set_default_timeout(10000)

    page.goto(f"{frontend_url}/item/{extracted_activity.stableTargetId}")
    page_body = page.get_by_test_id("page-body")
    expect(page_body).to_be_visible()
    return page


@pytest.mark.integration
def test_edit_page_updates_nav_bar(edit_page: Page) -> None:
    page = edit_page
    nav_bar = page.get_by_test_id("nav-bar")
    page.screenshot(path="tests_edit_test_main-test_edit_page_updates_nav_bar.png")
    expect(nav_bar).to_be_visible()
    nav_item = nav_bar.locator(".nav-item").all()[2]
    expect(nav_item).to_contain_text("Edit")
    expect(nav_item).to_have_class(re.compile("rt-underline-always"))


@pytest.mark.integration
def test_edit_page_renders_heading(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    heading = page.get_by_test_id("edit-heading")
    expect(heading).to_be_visible()
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_heading.png")
    expect(heading).to_have_text(re.compile(r"Aktivität 1\s*DE"))

    connector = BackendApiConnector.get()
    connector.update_rule_set(
        extracted_activity.stableTargetId,
        ActivityRuleSetRequest(
            additive=AdditiveActivity(
                title=[Text(value="New title who dis?", language=None)]
            ),
            subtractive=SubtractiveActivity(
                title=[Text(value="Aktivität 1", language=TextLanguage.DE)],
            ),
        ),
    )
    page.reload()
    heading = page.get_by_test_id("edit-heading")
    expect(heading).to_be_visible()
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_new_heading.png")
    expect(heading).to_have_text(re.compile(r"New title*"))


@pytest.mark.integration
def test_edit_page_renders_fields(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    funding_program = page.get_by_test_id("field-fundingProgram-name")
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_fields.png")
    expect(funding_program).to_be_visible()
    expect(page.get_by_role("row")).to_have_count(
        len(MERGEABLE_FIELDS_BY_CLASS_NAME[extracted_activity.entityType])
    )


@pytest.mark.integration
def test_edit_page_renders_primary_sources(
    edit_page: Page,
    extracted_activity: ExtractedActivity,
    dummy_data_by_stable_target_id: dict[Identifier, AnyExtractedModel],
) -> None:
    page = edit_page
    had_primary_source = dummy_data_by_stable_target_id[
        extracted_activity.hadPrimarySource
    ]
    assert type(had_primary_source) is ExtractedPrimarySource

    primary_source = page.get_by_test_id(
        f"primary-source-title-{extracted_activity.hadPrimarySource}-name"
    )
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_renders_primary_sources.png"
    )
    expect(primary_source).to_be_visible()
    expect(primary_source).to_contain_text(had_primary_source.title[0].value)
    link = primary_source.get_by_role("link")
    expect(link).to_have_attribute(
        "data-href", f"/item/{extracted_activity.hadPrimarySource}"
    )


@pytest.mark.integration
def test_edit_page_renders_text(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    text = page.get_by_test_id(f"value-title-{extracted_activity.hadPrimarySource}-0")
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_text.png")
    expect(text).to_be_visible()
    expect(text).to_contain_text("Aktivität 1")  # text value
    expect(text).to_contain_text("DE")  # language badge


@pytest.mark.integration
def test_edit_page_renders_vocab(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    theme = page.get_by_test_id(f"value-theme-{extracted_activity.hadPrimarySource}-0")
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_vocab.png")
    expect(theme).to_be_visible()
    expect(theme).to_contain_text("INFECTIOUS_DISEASES_AND_EPIDEMIOLOGY")  # theme value
    expect(theme).to_contain_text("Theme")  # vocabulary name


@pytest.mark.integration
def test_edit_page_renders_link(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    website_0 = page.get_by_test_id(
        f"value-website-{extracted_activity.hadPrimarySource}-0"
    )
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_link.png")
    expect(website_0).to_be_visible()
    link_0 = website_0.get_by_role("link")
    expect(link_0).to_contain_text("Activity Homepage")  # link title
    expect(link_0).to_have_attribute("href", "https://activity-1")  # link href
    expect(link_0).to_have_attribute("target", "_blank")  # external link

    website_1 = page.get_by_test_id(
        f"value-website-{extracted_activity.hadPrimarySource}-1"
    )
    expect(website_1).to_be_visible()
    link_1 = website_1.get_by_role("link")
    expect(link_1).to_contain_text("https://activity-homepage-1")  # link title
    expect(link_1).to_have_attribute("href", "https://activity-homepage-1")  # link href
    expect(link_1).to_have_attribute("target", "_blank")  # external link


@pytest.mark.integration
def test_edit_page_renders_temporal(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    start = page.get_by_test_id(f"value-start-{extracted_activity.hadPrimarySource}-0")
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_temporal.png")
    expect(start).to_be_visible()
    expect(start).to_contain_text("1999-12-24")  # temporal localization


@pytest.mark.integration
def test_edit_page_resolves_identifier(
    edit_page: Page,
    dummy_data_by_stable_target_id: dict[Identifier, AnyExtractedModel],
    extracted_activity: ExtractedActivity,
) -> None:
    page = edit_page
    extracted_organizational_unit = dummy_data_by_stable_target_id[
        extracted_activity.contact[1]
    ]
    assert type(extracted_organizational_unit) is ExtractedOrganizationalUnit

    contact = page.get_by_test_id(
        f"value-contact-{extracted_activity.hadPrimarySource}-1"
    )
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_identifier.png")
    expect(contact).to_be_visible()
    link = contact.get_by_role("link")
    expect(link).to_contain_text(
        extracted_organizational_unit.shortName[0].value
    )  # resolved short name of unit
    expect(link).to_have_attribute(
        "data-href",
        f"/item/{extracted_activity.contact[1]}",  # link href
    )
    expect(link).not_to_have_attribute("target", "_blank")  # internal link


@pytest.mark.parametrize(
    ("switch_id"),
    [
        (r"switch-abstract-{had_primary_source}"),
        (r"switch-abstract-{had_primary_source}-1"),
        (r"switch-website-{had_primary_source}-1"),
    ],
    ids=["toggle primary source", "toggle value", "toggle link without text"],
)
@pytest.mark.integration
def test_edit_page_switch_roundtrip(
    edit_page: Page, extracted_activity: ExtractedActivity, switch_id: str
) -> None:
    switch_id = switch_id.format(had_primary_source=extracted_activity.hadPrimarySource)
    test_id = f"tests_edit_test_main-test_edit_page_switch_roundtrip_{switch_id}"
    page = edit_page

    # verify initial state: toggle is enabled
    switch = page.get_by_test_id(switch_id)
    expect(switch).to_have_count(1)
    switch.scroll_into_view_if_needed()
    page.screenshot(path=f"{test_id}-onload.png")
    expect(switch).to_be_visible()
    expect(switch).to_have_attribute("data-state", "checked")

    # click on the toggle to disable the primary source / specific value
    switch.click()
    expect(switch).to_have_attribute("data-state", "unchecked")
    page.screenshot(path=f"{test_id}-disabled.png")

    # click on the save button and verify the toast
    submit = page.get_by_test_id("submit-button")
    submit.scroll_into_view_if_needed()
    submit.click()
    toast = page.locator(".editor-toast").first
    expect(toast).to_be_visible()
    expect(toast).to_contain_text("Saved")
    page.screenshot(path=f"{test_id}-toast_1.png")

    # force a page reload
    page.reload()

    # verify the state after first saving: toggle is off
    switch = page.get_by_test_id(switch_id)
    expect(switch).to_have_count(1)
    switch.scroll_into_view_if_needed()
    page.screenshot(path=f"{test_id}-reload_1.png")
    expect(switch).to_be_visible()
    expect(switch).to_have_attribute("data-state", "unchecked")

    # click on the toggle to re-enable the primary source / specific value
    switch.click()
    expect(switch).to_have_attribute("data-state", "checked")
    page.screenshot(path=f"{test_id}-enabled.png")

    # click on the save button again and verify the toast again
    submit = page.get_by_test_id("submit-button")
    submit.scroll_into_view_if_needed()
    submit.click()
    toast = page.locator(".editor-toast").first
    expect(toast).to_be_visible()
    expect(toast).to_contain_text("Saved")
    page.screenshot(path=f"{test_id}-toast_2.png")

    # force a page reload again
    page.reload()

    # verify the state after second saving: toggle is on again
    switch = page.get_by_test_id(switch_id)
    page.screenshot(path=f"{test_id}-reload_2.png")
    expect(switch).to_have_count(1)
    expect(switch).to_be_visible()
    expect(switch).to_have_attribute("data-state", "checked")


@pytest.mark.integration
def test_edit_page_renders_new_additive_button(edit_page: Page) -> None:
    page = edit_page
    new_additive_button = page.get_by_test_id(
        "new-additive-fundingProgram-00000000000000"
    )
    new_additive_button.scroll_into_view_if_needed()
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_renders_new_additive_button.png"
    )
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()

    additive_rule_input = page.get_by_test_id("additive-rule-fundingProgram-0-text")
    additive_rule_input.scroll_into_view_if_needed()
    expect(additive_rule_input).to_be_visible()


@pytest.mark.integration
def test_edit_page_renders_remove_additive_button(edit_page: Page) -> None:
    page = edit_page
    new_additive_button = page.get_by_test_id(
        "new-additive-fundingProgram-00000000000000"
    )
    new_additive_button.scroll_into_view_if_needed()
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_renders_remove_additive_button.png"
    )
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()

    remove_additive_rule_button = page.get_by_test_id(
        "additive-rule-fundingProgram-0-remove-button"
    )
    expect(remove_additive_rule_button).to_be_visible()


@pytest.mark.integration
def test_edit_page_renders_text_input(edit_page: Page) -> None:
    page = edit_page
    new_additive_button = page.get_by_test_id("new-additive-shortName-00000000000000")
    new_additive_button.scroll_into_view_if_needed()
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_text_input.png")

    text_input = page.get_by_test_id("additive-rule-shortName-0-text")
    expect(text_input).to_be_visible()
    badge_select = page.get_by_test_id("additive-rule-shortName-0-badge")
    expect(badge_select).to_be_visible()


@pytest.mark.integration
def test_edit_page_renders_textarea_input(edit_page: Page) -> None:
    page = edit_page
    new_additive_button = page.get_by_test_id(
        "new-additive-alternativeTitle-00000000000000"
    )
    new_additive_button.scroll_into_view_if_needed()
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_renders_textarea_input.png"
    )

    textarea_input = page.get_by_test_id("additive-rule-alternativeTitle-0-text")
    expect(textarea_input).to_be_visible()
    assert textarea_input.evaluate("el => el.tagName.toLowerCase()") == "textarea"

    badge_select = page.get_by_test_id("additive-rule-alternativeTitle-0-badge")
    expect(badge_select).to_be_visible()


@pytest.mark.integration
def test_edit_page_renders_identifier_input(edit_page: Page) -> None:
    page = edit_page
    new_additive_button = page.get_by_test_id(
        "new-additive-involvedUnit-00000000000000"
    )
    new_additive_button.scroll_into_view_if_needed()
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_renders_identifier_input.png"
    )

    identifier_input = page.get_by_test_id("additive-rule-involvedUnit-0-identifier")
    expect(identifier_input).to_be_visible()


@pytest.mark.integration
def test_edit_page_resolves_additive_identifier(
    edit_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    page = edit_page
    new_additive_button = page.get_by_test_id(
        "new-additive-involvedUnit-00000000000000"
    )
    new_additive_button.scroll_into_view_if_needed()
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()

    organizational_unit = dummy_data_by_identifier_in_primary_source["ou-1"]
    assert isinstance(organizational_unit, ExtractedOrganizationalUnit)
    identifier_input = page.get_by_test_id("additive-rule-involvedUnit-0-identifier")
    expect(identifier_input).to_be_visible()
    identifier_input.fill(organizational_unit.stableTargetId)
    edit_button = page.get_by_test_id("edit-toggle-involvedUnit-00000000000000-0")
    edit_button.click()

    # verify identifier is correctly rendered
    identifier_card = page.get_by_test_id("additive-rule-involvedUnit-0")
    rendered_identifier = identifier_card.get_by_role(
        "link", name=organizational_unit.shortName[0].value
    )
    expect(rendered_identifier).to_have_count(1)
    assert (
        rendered_identifier.first.get_attribute("data-href")
        == f"/item/{organizational_unit.stableTargetId}"
    )

    # assert raw identifier value is retained
    edit_button.click()
    identifier_input = page.get_by_test_id("additive-rule-involvedUnit-0-identifier")
    expect(identifier_input).to_have_attribute(
        "value", organizational_unit.stableTargetId
    )


@pytest.mark.integration
def test_edit_page_renders_link_input(edit_page: Page) -> None:
    page = edit_page
    new_additive_button = page.get_by_test_id("new-additive-website-00000000000000")
    new_additive_button.scroll_into_view_if_needed()
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_link_input.png")

    text_input = page.get_by_test_id("additive-rule-website-0-text")
    expect(text_input).to_be_visible()
    badge_select = page.get_by_test_id("additive-rule-website-0-badge")
    expect(badge_select).to_be_visible()
    href_input = page.get_by_test_id("additive-rule-website-0-href")
    expect(href_input).to_be_visible()


@pytest.mark.integration
def test_edit_page_renders_vocabulary_input(edit_page: Page) -> None:
    page = edit_page
    new_additive_button = page.get_by_test_id(
        "new-additive-activityType-00000000000000"
    )
    new_additive_button.scroll_into_view_if_needed()
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_renders_vocabulary_input_closed.png"
    )

    badge_select = page.get_by_test_id("additive-rule-activityType-0-badge")
    expect(badge_select).to_be_visible()
    expect(page.get_by_text("THIRD_PARTY_FUNDED_PROJECT")).to_be_visible()
    badge_select.focus()
    page.keyboard.press("ArrowDown")
    page.keyboard.press("ArrowDown")
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_renders_vocabulary_input_open.png"
    )
    page.keyboard.press("Enter")
    page.locator("body").focus()
    expect(page.get_by_text("INTERNAL_PROJECT_ENDEAVOR")).to_be_visible()


@pytest.mark.integration
def test_edit_page_renders_temporal_input(edit_page: Page) -> None:
    page = edit_page
    new_additive_button = page.get_by_test_id("new-additive-end-00000000000000")
    new_additive_button.scroll_into_view_if_needed()
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_renders_temporal_input_closed.png"
    )

    badge_select = page.get_by_test_id("additive-rule-end-0-badge")
    expect(badge_select).to_be_visible()
    expect(page.get_by_text("year")).to_be_visible()
    badge_select.click()
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_renders_temporal_input_open.png"
    )
    precision_options = page.get_by_role("group").get_by_role("option")
    expect(precision_options).to_have_count(3)
    expect(precision_options).to_have_text(["year", "month", "day"])


@pytest.mark.integration
def test_edit_page_additive_rule_roundtrip(
    edit_page: Page,
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    page = edit_page
    test_id = "tests_edit_test_main-test_edit_page_additive_rule_roundtrip"

    # click button for new additive rule on contact field
    new_additive_button = page.get_by_test_id("new-additive-contact-00000000000000")
    new_additive_button.scroll_into_view_if_needed()
    page.screenshot(path=f"{test_id}-on_load.png")
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()

    # fill a string into the additive rule input
    input_id = "additive-rule-contact-0-identifier"
    additive_rule_input = page.get_by_test_id(input_id)
    expect(additive_rule_input).to_be_visible()
    contact_point_2 = dummy_data_by_identifier_in_primary_source["cp-2"]
    rule_value = contact_point_2.stableTargetId
    additive_rule_input.fill(rule_value)
    page.screenshot(path=f"{test_id}-input-filled.png")

    # save the rule-set
    submit_button = page.get_by_test_id("submit-button")
    submit_button.scroll_into_view_if_needed()
    submit_button.click()

    # click on the save button and verify the toast
    toast = page.locator(".editor-toast").first
    expect(toast).to_be_visible()
    expect(toast).to_contain_text("Saved")
    page.screenshot(path=f"{test_id}-toast.png")

    # force a page reload
    page.reload()

    # verify the state after first saving: additive rule is present
    rendered_input_id = "additive-rule-contact-0"
    additive_rule_rendered = page.get_by_test_id(rendered_input_id)
    expect(additive_rule_rendered).to_have_count(1)
    additive_rule_rendered.scroll_into_view_if_needed()
    page.screenshot(path=f"{test_id}-reload_1.png")
    expect(additive_rule_rendered).to_be_visible()

    # click edit button
    edit_button = page.get_by_test_id("edit-toggle-contact-00000000000000-0")
    edit_button.scroll_into_view_if_needed()
    page.screenshot(path=f"{test_id}-on_load.png")
    expect(edit_button).to_be_visible()
    edit_button.click()

    # verify content of additive rule
    additive_rule_input = page.get_by_test_id(input_id)
    expect(additive_rule_input).to_be_visible()
    expect(additive_rule_input).to_have_attribute("value", rule_value)

    # now remove the additive rule for a full roundtrip
    remove_additive_rule_button = page.get_by_test_id(
        "additive-rule-contact-0-remove-button"
    )
    expect(remove_additive_rule_button).to_be_visible()
    remove_additive_rule_button.click()

    # check the rule input is gone
    additive_rule_rendered = page.get_by_test_id(rendered_input_id)
    expect(additive_rule_rendered).to_have_count(0)

    # click on the save button and force a page reload again
    submit_button = page.get_by_test_id("submit-button")
    submit_button.scroll_into_view_if_needed()
    submit_button.click()
    page.wait_for_timeout(30000)  # wait for save operation
    page.reload()

    # check the rule input is still gone
    page.get_by_test_id("field-contact").scroll_into_view_if_needed()
    page.screenshot(path=f"{test_id}-reload_2.png")
    additive_rule_rendered = page.get_by_test_id(rendered_input_id)
    expect(additive_rule_rendered).to_have_count(0)


@pytest.mark.integration
def test_required_fields_red_asterisk(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    expected_required_fields = [
        "contact",
        "responsibleUnit",
        "title",
    ]
    expected_optional_fields = [
        "abstract",
        "activityType",
        "alternativeTitle",
        "documentation",
        "end",
        "externalAssociate",
        "funderOrCommissioner",
        "fundingProgram",
        "involvedPerson",
        "involvedUnit",
        "isPartOfActivity",
        "publication",
        "shortName",
        "start",
        "succeeds",
        "theme",
        "website",
    ]

    required_mergeable_fields = get_required_mergeable_field_names(extracted_activity)
    assert set(required_mergeable_fields) == set(expected_required_fields)

    merged_type = ensure_prefix(extracted_activity.stemType, "Merged")
    required_fields = set(REQUIRED_FIELDS_BY_CLASS_NAME[merged_type])
    mergeable_fields = set(MERGEABLE_FIELDS_BY_CLASS_NAME[merged_type])
    optional_mergeable_fields = sorted(mergeable_fields - required_fields)
    assert set(optional_mergeable_fields) == set(expected_optional_fields)

    for field_name in expected_required_fields + expected_optional_fields:
        field = edit_page.get_by_test_id(f"field-{field_name}-name")
        expect(field).to_be_visible()

        asterisk = field.get_by_text("*", exact=True)
        if field_name in expected_required_fields:
            expect(asterisk).to_be_visible()
            expect(asterisk).to_have_css("color", "rgb(255, 99, 71)")
        else:
            expect(asterisk).to_have_count(0)


@pytest.mark.integration
def test_deactivate_all_switch(edit_page: Page) -> None:
    page = edit_page

    expect(page.get_by_test_id("deactivate-all-switch")).to_be_checked()
    page.get_by_test_id("deactivate-all-switch").click()
    expect(page.get_by_test_id("deactivate-all-switch")).not_to_be_checked()
    page.screenshot(path="tests_edit_test_main-test_deactivate_all_switch-clicked.png")

    last_switch = None
    all_switches = page.get_by_role("switch").all()

    for switch in all_switches:
        expect(switch).not_to_be_checked()
        last_switch = switch

    assert last_switch
    last_switch.click()
    last_switch.screenshot(
        path="tests_edit_test_main-test_deactivate_all_last-switch-click.png"
    )

    expect(page.get_by_test_id("deactivate-all-switch")).to_be_checked()


@pytest.mark.integration
def test_edit_page_warn_tab_close(edit_page: Page) -> None:
    page = edit_page

    # ensure navigation without changes is working
    page.goto("https://www.rki.de")
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_warn_tab_close-rki_website.png"
    )
    assert "https://www.rki.de" in page.url

    # back to edit site
    page.go_back()
    page.wait_for_url("**/item/**")
    page.wait_for_selector(
        "[data-testid='new-additive-alternativeTitle-00000000000000']"
    )
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_warn_tab_close-back_on_edit.png"
    )

    # change a value
    page.get_by_test_id("new-additive-alternativeTitle-00000000000000").click()
    page.get_by_test_id("additive-rule-alternativeTitle-0-text").fill(
        "new alternative title"
    )
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_warn_tab_close-page_with_changes.png"
    )

    handle_dialog_called: list[bool] = []

    def _handle_dialog(dialog: Dialog) -> None:
        # damn i love python
        nonlocal handle_dialog_called

        assert dialog.type == "beforeunload"
        handle_dialog_called.append(True)

        # stay on the side
        dialog.dismiss()

    page.on("dialog", _handle_dialog)

    # won't work cuz we dismiss the dialog
    with pytest.raises(Exception, match="Timeout"):
        page.goto("https://www.rki.de", timeout=3000)

    # ensure still on edit site and dialog was called
    assert "/item/" in page.url
    assert len(handle_dialog_called) == 1
    assert handle_dialog_called[0]

    # after save we should navigate again without dialog
    page.get_by_test_id("submit-button").click()
    page.wait_for_selector(".editor-toast")
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_warn_tab_close-save_toast.png"
    )

    page.goto("https://www.rki.de")
    assert "https://www.rki.de" in page.url
    assert len(handle_dialog_called) == 1


@pytest.mark.integration
def test_edit_page_submit_button_disabled_while_submitting(edit_page: Page) -> None:
    edit_page.get_by_test_id("new-additive-alternativeTitle-00000000000000").click()
    edit_page.get_by_test_id("additive-rule-alternativeTitle-0-text").fill(
        "new alternative title"
    )
    # check default state
    submit_button = edit_page.get_by_test_id("submit-button")
    expect(submit_button).to_have_text(re.compile(r"Save .*"))
    expect(submit_button).not_to_be_disabled()

    # submit item
    submit_button.click()
    expect(submit_button).to_have_text(re.compile(r"Saving .*"))
    expect(submit_button).to_be_disabled()

    # check if back in default state after saving
    edit_page.wait_for_timeout(30000)
    expect(submit_button).to_have_text(re.compile(r"Save .*"))
    expect(submit_button).not_to_be_disabled()


@pytest.mark.integration
def test_edit_page_navigation_unsaved_changes_warning_cancel_save_and_navigate(
    edit_page: Page,
) -> None:
    page = edit_page

    # do some changes
    page.get_by_test_id("new-additive-alternativeTitle-00000000000000").click()
    page.get_by_test_id("additive-rule-alternativeTitle-0-text").fill(
        "new alternative title"
    )

    # try to navigate to search page (via navbar)
    nav_bar = page.get_by_test_id("nav-bar")
    search_nav = nav_bar.get_by_text("search")
    search_nav.click()

    # now dialog should appear
    dialog = page.get_by_role("alertdialog", name="Unsaved changes")
    expect(dialog).to_be_visible()

    # cancel the navigation and check if url is still edit page
    dialog.get_by_role("button", name="Stay here").click()
    expect(page).to_have_url(re.compile("/item/.*"))

    # click save changes
    page.get_by_test_id("submit-button").click()
    page.wait_for_selector(".editor-toast")

    # navigate to search page (should work)
    search_nav.click()
    expect(dialog).to_be_hidden()
    page.wait_for_url(re.compile("/"))


@pytest.mark.integration
def test_edit_page_navigation_unsaved_changes_warning_discard_changes_and_navigate(
    edit_page: Page,
) -> None:
    page = edit_page

    # do some changes
    page.get_by_test_id("new-additive-alternativeTitle-00000000000000").click()
    page.get_by_test_id("additive-rule-alternativeTitle-0-text").fill(
        "new alternative title"
    )

    # try to navigate to search page (via navbar)
    nav_bar = page.get_by_test_id("nav-bar")
    search_nav = nav_bar.get_by_text("search")
    search_nav.click()

    # now dialog should appear
    dialog = page.get_by_role("alertdialog", name="Unsaved changes")
    expect(dialog).to_be_visible()

    # discard changes and expect navigation (url is search page url)
    dialog.get_by_role("button", name="Navigate away").click()
    expect(page).to_have_url(re.compile("/"))
