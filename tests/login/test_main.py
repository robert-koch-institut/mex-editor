from mex.editor.login.main import index


def test_index() -> None:
    index_component = index()
    assert "Login" in index_component.render()["contents"]
