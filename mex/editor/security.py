from secrets import compare_digest
from urllib.parse import urlsplit

from ldap3 import AUTO_BIND_NO_TLS, Connection, Server
from ldap3.core.exceptions import LDAPBindError
from ldap3.utils.dn import escape_rdn

from mex.common.logging import logger
from mex.editor.settings import EditorSettings


def has_write_access_mex(username: str, password: str) -> bool:
    """Verify if provided credentials have write access."""
    settings = EditorSettings.get()
    write_user_db = settings.editor_user_database["write"]
    if write_user := write_user_db.get(username):
        return compare_digest(
            password.encode("ascii"), write_user.get_secret_value().encode("ascii")
        )
    return False


def has_write_access_ldap(username: str, password: str) -> bool:
    """Verify if provided credentials have ldap write access."""
    settings = EditorSettings.get()
    url = urlsplit(settings.ldap_url.get_secret_value())
    host = str(url.hostname)
    port = int(url.port) if url.port else None
    server = Server(host, port, use_ssl=True)
    username = username.split("@")[0]
    username = escape_rdn(username)
    try:
        with Connection(
            server,
            user=f"{username}@rki.local",
            password=password,
            auto_bind=AUTO_BIND_NO_TLS,
            read_only=True,
        ) as connection:
            availability = connection.server.check_availability()
            if availability is True:
                return True
            logger.error(availability)
            return False

    except LDAPBindError as error:
        logger.error(f"LDAP bind error: {error}")
        return False


def has_read_access_mex(username: str, password: str) -> bool:
    """Verify if provided credentials have read access."""
    settings = EditorSettings.get()
    read_user_db = settings.editor_user_database["read"]
    if read_user := read_user_db.get(username):
        return compare_digest(
            password.encode("ascii"), read_user.get_secret_value().encode("ascii")
        )
    return has_write_access_mex(username, password)
