from urllib.parse import urlsplit

import pytest

from mex.editor.security import (
    has_read_access_mex,
    has_write_access_ldap,
    has_write_access_mex,
)
from mex.editor.settings import EditorSettings


def test_has_write_access_mex() -> None:
    assert has_write_access_mex("no_account", "who_dis?") is False
    assert has_write_access_mex("reader", "reader_pass") is False
    assert has_write_access_mex("writer", "writer_pass") is True


def test_has_read_access_mex() -> None:
    assert has_read_access_mex("no_account", "who_dis?") is False
    assert has_read_access_mex("reader", "reader_pass") is True
    assert has_read_access_mex("writer", "writer_pass") is True


@pytest.mark.external
@pytest.mark.integration
def test_has_write_access_ldap() -> None:
    settings = EditorSettings.get()
    url = urlsplit(settings.ldap_url.get_secret_value())
    assert has_write_access_ldap(f"{url.username}", f"{url.password}") is True
    assert has_write_access_ldap(f"{url.username}@wasd.def", f"{url.password}") is True
    assert has_write_access_ldap(f"{url.username}", "wrong_pass") is False
    assert has_write_access_ldap("no_account", "who_dis?") is False
