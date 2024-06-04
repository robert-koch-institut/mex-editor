from mex.editor.edit.main import index


def test_index() -> None:
    index_component = index()
    assert index_component.children[0].id == "navbar"
    index_body = index_component.children[1]
    assert "state.item_id" in index_body.children[0].render()["contents"]
