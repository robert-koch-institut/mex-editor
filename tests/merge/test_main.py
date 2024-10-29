import pytest
from playwright.sync_api import Page, expect


@pytest.mark.integration
def test_index(writer_user_page: Page) -> None:
    page = writer_user_page

    # load page and establish section is visible
    page.goto("http://localhost:3000/merge")
    heading = page.get_by_test_id("merge-heading")
    expect(heading).to_be_visible()
    page.screenshot(path="tests_merge_test_main-test_index-on-load.png")

    # check heading is showing
    heading = page.get_by_test_id("merge-heading")
    expect(heading).to_be_visible()
    assert heading.inner_text() == "Merge"
