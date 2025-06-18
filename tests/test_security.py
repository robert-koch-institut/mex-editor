from urllib.parse import urlsplit

import pytest

from mex.editor.security import has_read_access, has_write_access, has_write_access_ldap
from mex.editor.settings import EditorSettings


def test_has_write_access() -> None:
    assert has_write_access("no_account", "who_dis?") is False
    assert has_write_access("reader", "reader_pass") is False
    assert has_write_access("writer", "writer_pass") is True


def test_has_read_access() -> None:
    assert has_read_access("no_account", "who_dis?") is False
    assert has_read_access("reader", "reader_pass") is True
    assert has_read_access("writer", "writer_pass") is True


@pytest.mark.integration
def test_has_write_access_ldap() -> None:
    settings = EditorSettings.get()
    url = urlsplit(settings.ldap_url.get_secret_value())
    assert has_write_access_ldap(url.username, url.password) is True
    assert has_write_access_ldap(f"{url.username}@wasd.def", url.password) is True
    assert has_write_access_ldap(url.username, "wrong_pass") is False
    assert has_write_access_ldap("no_account", "who_dis?") is False
