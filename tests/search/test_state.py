import pytest

from mex.editor.search.state import SearchState


@pytest.mark.usefixtures("mocked_backend")
def test_search_state_refresh() -> None:
    state = SearchState()
    assert state.total == 0

    state.refresh()
    assert state.total == 2
