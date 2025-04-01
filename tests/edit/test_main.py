import re
from typing import cast

import pytest
from playwright.sync_api import Page, expect

from mex.common.fields import MERGEABLE_FIELDS_BY_CLASS_NAME
from mex.common.models import AnyExtractedModel, ExtractedActivity


@pytest.fixture
def extracted_activity(load_dummy_data: list[AnyExtractedModel]) -> ExtractedActivity:
    return cast("ExtractedActivity", load_dummy_data[-1])


@pytest.fixture
def edit_page(
    frontend_url: str, writer_user_page: Page, extracted_activity: ExtractedActivity
) -> Page:
    page = writer_user_page
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
    nav_item = nav_bar.locator(".nav-item").all()[1]
    expect(nav_item).to_contain_text("Edit")
    expect(nav_item).to_have_class(re.compile("rt-underline-always"))


@pytest.mark.integration
def test_edit_page_renders_heading(edit_page: Page) -> None:
    page = edit_page
    heading = page.get_by_test_id("edit-heading")
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_heading.png")
    expect(heading).to_be_visible()
    assert re.match(r"Aktivität 1\s*de", heading.inner_text())


@pytest.mark.integration
def test_edit_page_renders_fields(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    funding_program = page.get_by_test_id("field-fundingProgram-name")
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_fields.png")
    expect(funding_program).to_be_visible()
    all_fields = page.get_by_role("row").all()
    assert len(all_fields) == len(
        MERGEABLE_FIELDS_BY_CLASS_NAME[extracted_activity.entityType]
    )


@pytest.mark.integration
def test_edit_page_renders_primary_sources(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    primary_source = page.get_by_test_id(
        f"primary-source-title-{extracted_activity.hadPrimarySource}-name"
    )
    page.screenshot(
        path="tests_edit_test_main-test_edit_page_renders_primary_sources.png"
    )
    expect(primary_source).to_be_visible()
    expect(primary_source).to_contain_text(extracted_activity.hadPrimarySource)
    link = primary_source.get_by_role("link")
    expect(link).to_have_attribute(
        "href", f"/item/{extracted_activity.hadPrimarySource}/"
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
    expect(text).to_contain_text("de")  # language badge


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
    website = page.get_by_test_id(
        f"value-website-{extracted_activity.hadPrimarySource}-0"
    )
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_link.png")
    expect(website).to_be_visible()
    link = website.get_by_role("link")
    expect(link).to_contain_text("Activity Homepage")  # link title
    expect(link).to_have_attribute("href", "https://activity-1")  # link href
    expect(link).to_have_attribute("target", "_blank")  # external link


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
def test_edit_page_renders_identifier(
    edit_page: Page, extracted_activity: ExtractedActivity
) -> None:
    page = edit_page
    contact = page.get_by_test_id(
        f"value-contact-{extracted_activity.hadPrimarySource}-2"
    )
    page.screenshot(path="tests_edit_test_main-test_edit_page_renders_identifier.png")
    expect(contact).to_be_visible()
    link = contact.get_by_role("link")
    expect(link).to_contain_text(extracted_activity.contact[2])  # not resolved yet
    expect(link).to_have_attribute(
        "href",
        f"/item/{extracted_activity.contact[2]}/",  # link href
    )
    expect(link).not_to_have_attribute("target", "_blank")  # internal link


@pytest.mark.parametrize(
    ("switch_id"),
    [
        (r"{prefix}"),
        (r"{prefix}-1"),
    ],
    ids=["toggle primary source", "toggle value"],
)
@pytest.mark.integration
def test_edit_page_switch_roundtrip(
    edit_page: Page, extracted_activity: ExtractedActivity, switch_id: str
) -> None:
    prefix = f"switch-abstract-{extracted_activity.hadPrimarySource}"
    test_id = switch_id.format(
        prefix="tests_edit_test_main-test_edit_page_switch_roundtrip"
    )
    switch_id = switch_id.format(prefix=prefix)
    page = edit_page

    # verify initial state: toggle is enabled
    switch = page.get_by_test_id(switch_id)
    page.screenshot(path=f"{test_id}-onload.png")
    expect(switch).to_have_count(1)
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
def test_edit_page_additive_rule_roundtrip(edit_page: Page) -> None:
    page = edit_page
    test_id = "tests_edit_test_main-test_edit_page_additive_rule_roundtrip"

    # click button for new additive rule on fundingProgram field
    new_additive_button = page.get_by_test_id(
        "new-additive-fundingProgram-00000000000000"
    )
    new_additive_button.scroll_into_view_if_needed()
    page.screenshot(path=f"{test_id}-on_load.png")
    expect(new_additive_button).to_be_visible()
    new_additive_button.click()

    # fill a string into the additive rule input
    input_id = "additive-rule-fundingProgram-0-text"
    additive_rule_input = page.get_by_test_id(input_id)
    expect(additive_rule_input).to_be_visible()
    rule_value = "FundEverything e.V."
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
    additive_rule_input = page.get_by_test_id(input_id)
    expect(additive_rule_input).to_have_count(1)
    additive_rule_input.scroll_into_view_if_needed()
    page.screenshot(path=f"{test_id}-reload_1.png")
    expect(additive_rule_input).to_be_visible()
    expect(additive_rule_input).to_have_attribute("value", rule_value)

    # now remove the additive rule for a full roundtrip
    remove_additive_rule_button = page.get_by_test_id(
        "additive-rule-fundingProgram-0-remove-button"
    )
    expect(remove_additive_rule_button).to_be_visible()
    remove_additive_rule_button.click()

    # check the rule input is gone
    additive_rule_input = page.get_by_test_id(input_id)
    expect(additive_rule_input).to_have_count(0)

    # click on the save button and force a page reload again
    submit_button = page.get_by_test_id("submit-button")
    submit_button.scroll_into_view_if_needed()
    submit_button.click()
    page.reload()

    # check the rule input is still gone
    page.get_by_test_id("field-fundingProgram").scroll_into_view_if_needed()
    page.screenshot(path=f"{test_id}-reload_2.png")
    additive_rule_input = page.get_by_test_id(input_id)
    expect(additive_rule_input).to_have_count(0)
