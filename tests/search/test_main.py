from mex.editor.search.main import index


def test_index() -> None:
    index_component = index()
    assert index_component.children[0].id == "navbar"
    index_body = index_component.children[1]
    assert "search here" in index_body.children[0].render()["contents"]
