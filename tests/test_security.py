from mex.editor.security import has_read_access, has_write_access


def test_has_write_access() -> None:
    assert has_write_access("no_account", "who_dis?") is False
    assert has_write_access("reader", "reader_pass") is False
    assert has_write_access("writer", "writer_pass") is True


def test_has_read_access() -> None:
    assert has_read_access("no_account", "who_dis?") is False
    assert has_read_access("reader", "reader_pass") is True
    assert has_read_access("writer", "writer_pass") is True
