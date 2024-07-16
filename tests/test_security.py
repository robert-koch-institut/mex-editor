import pytest
from pytest import MonkeyPatch

from mex.editor.security import has_read_access, has_write_access
from mex.editor.settings import EditorSettings


@pytest.fixture(autouse=True)
def patch_editor_user_database(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        EditorSettings,
        "editor_user_database",
        {"read": {"reader": "reader_pass"}, "write": {"writer": "writer_pass"}},
    )


def test_has_write_access() -> None:
    assert has_write_access("no_account", "who_dis?") is False
    assert has_write_access("reader", "reader_pass") is False
    assert has_write_access("writer", "writer_pass") is True


def test_has_read_access() -> None:
    assert has_read_access("no_account", "who_dis?") is False
    assert has_read_access("reader", "reader_pass") is True
    assert has_read_access("writer", "writer_pass") is True
