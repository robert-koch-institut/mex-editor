from mex.editor.login.state import LoginMExState
from mex.editor.state import State


def test_login_state_login_success() -> None:
    state = LoginMExState(
        username="writer",
        password="writer_pass",  # noqa: S106
        parent_state=State(),
    )

    assert "/" in str(state.login())
    assert state.user_mex
    assert state.user_mex.dict() == {
        "name": "writer",
        "authorization": "Basic d3JpdGVyOndyaXRlcl9wYXNz",
        "write_access": True,
    }


def test_login_state_login_error() -> None:
    state = LoginMExState(
        username="not_a_user",
        password="not_a_pass",  # noqa: S106
        parent_state=State(),
    )

    assert "Invalid credentials" in str(state.login())
    assert not state.user_mex


def test_login_state_redirect_to_original_url() -> None:
    state = LoginMExState(
        username="writer",
        password="writer_pass",  # noqa: S106
        parent_state=State(target_path_after_login="/some-url/"),
    )
    assert "/some-url/" in str(state.login())
    assert state.user_mex
