from pytest import MonkeyPatch

from mex.editor.edit.state import EditState


def test_edit_state_item_id(monkeypatch: MonkeyPatch) -> None:
    state = EditState()
    assert state.item_id == "N/A"

    monkeypatch.setitem(state.router.page.params, "item_id", "123")
    assert state.item_id == "123"
