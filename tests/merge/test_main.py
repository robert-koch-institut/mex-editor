from mex.editor.merge.main import index


def test_index() -> None:
    index_component = index()
    assert index_component.children
