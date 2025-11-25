from mex.editor.security import (
    has_read_access_mex,
    has_write_access_mex,
)


def test_has_write_access_mex() -> None:
    assert has_write_access_mex("no_account", "who_dis?") is False
    assert has_write_access_mex("reader", "reader_pass") is False
    assert has_write_access_mex("writer", "writer_pass") is True


def test_has_read_access_mex() -> None:
    assert has_read_access_mex("no_account", "who_dis?") is False
    assert has_read_access_mex("reader", "reader_pass") is True
    assert has_read_access_mex("writer", "writer_pass") is True
