from mex.editor.login.main import index


def test_index() -> None:
    index_component = index()
    assert "Log in" in str(index_component.children[0])
