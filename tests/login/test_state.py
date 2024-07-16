from mex.editor.login.state import LoginState
from mex.editor.state import State


def test_login_state_login_success() -> None:
    state = LoginState(
        username="writer", password="writer_pass", parent_state=State()  # noqa: S106
    )

    assert "/" in str(state.login())
    assert state.user
    assert state.user.dict() == {
        "name": "writer",
        "authorization": "Basic d3JpdGVyOndyaXRlcl9wYXNz",
        "write_access": True,
    }


def test_login_state_login_error() -> None:
    state = LoginState(
        username="not_a_user", password="not_a_pass", parent_state=State()  # noqa: S106
    )

    assert "Invalid credentials" in str(state.login())
    assert not state.user
