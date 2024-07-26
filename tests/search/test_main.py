from mex.editor.search.main import index


def test_index() -> None:
    index_component = index()
    assert index_component.children
