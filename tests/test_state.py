from typing import Any

import pytest

from mex.editor.models import NavItem
from mex.editor.state import State, User


def test_state_logout() -> None:
    state = State(user_mex=User(name="Test", authorization="Auth", write_access=True))
    assert state.user_mex

    assert "/" in str(state.logout())
    assert state.user_mex is None


def test_state_check_login_pass() -> None:
    state = State(user_mex=User(name="Test", authorization="Auth", write_access=True))
    assert state.user_mex

    assert state.check_mex_login() is None


def test_state_check_login_fail() -> None:
    state = State()
    assert state.user_mex is None

    assert "/login" in str(state.check_mex_login())


@pytest.mark.parametrize(
    ("nav_item", "params", "expected"),
    [
        (
            NavItem(
                path="/",
                raw_path="/",
            ),
            {},
            "/",
        ),
        (
            NavItem(
                path="/thing/[thing_id]",
                raw_path="/thing/123",
            ),
            {"thing_id": "456"},
            "/thing/456",
        ),
        (
            NavItem(
                path="/thing/[thing_id]",
                raw_path="/thing/123",
            ),
            {"thing_id": "456", "some-param": "foo"},
            "/thing/456?some-param=foo",
        ),
        (
            NavItem(
                path="/things",
                raw_path="/things?oldParam=foo",
            ),
            {"newParam": ["bar", "batz"]},
            "/things?newParam=bar&newParam=batz",
        ),
        (
            NavItem(
                path="/students",
                raw_path="/students",
            ),
            {"name": "Robert'); DROP TABLE Students;--"},
            "/students?name=Robert%27%29%3B+DROP+TABLE+Students%3B--",
        ),
    ],
    ids=["empty", "single param", "merge params", "multi param", "url encoding"],
)
def test_update_raw_path(
    nav_item: NavItem, params: dict[str, Any], expected: str
) -> None:
    State._update_raw_path(nav_item, params)
    assert nav_item.raw_path == expected
