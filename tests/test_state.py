from mex.editor.state import State, User


def test_state_logout() -> None:
    state = State(user=User(name="Test", authorization="Auth", write_access=True))
    assert state.user

    assert "/" in str(state.logout())
    assert state.user is None


def test_state_check_login_pass() -> None:
    state = State(user=User(name="Test", authorization="Auth", write_access=True))
    assert state.user

    assert state.check_login() is None


def test_state_check_login_fail() -> None:
    state = State()
    assert state.user is None

    assert "/login" in str(state.check_login())
