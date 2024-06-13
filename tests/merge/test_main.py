from mex.editor.merge.main import index


def test_index() -> None:
    index_component = index()
    assert index_component.children[0].id == "navbar"
    index_body = index_component.children[1]
    assert "merge that" in index_body.children[0].render()["contents"]
