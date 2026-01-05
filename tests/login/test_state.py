from mex.editor.login.state import LoginMExState, LoginState
from mex.editor.state import State


def test_login_state_login_success() -> None:
    state = LoginMExState(
        parent_state=LoginState(
            username="writer",
            password="writer_pass",  # noqa: S106
            parent_state=State(target_path_after_login="/some-url/"),
        ),
    )  # type: ignore[call-arg]

    assert "/" in str(list(state.login)())  # type: ignore[call-overload]
    assert state.user_mex
    assert state.user_mex.dict() == {
        "name": "writer",
        "write_access": True,
    }


def test_login_state_login_error() -> None:
    state = LoginMExState(
        parent_state=LoginState(
            username="not_a_user",
            password="not_a_pass",  # noqa: S106
            parent_state=State(target_path_after_login="/some-url/"),
        ),
    )  # type: ignore[call-arg]

    event_str = str(list(state.login)())  # type: ignore[call-overload]
    assert "toast" in event_str
    assert "error" in event_str
    assert not state.user_mex


def test_login_state_redirect_to_original_url() -> None:
    state = LoginMExState(
        parent_state=LoginState(
            username="writer",
            password="writer_pass",  # noqa: S106
            parent_state=State(target_path_after_login="/some-url/"),
        ),
    )  # type: ignore[call-arg]
    assert "/some-url/" in str(list(state.login)())  # type: ignore[call-overload]
    assert state.user_mex
