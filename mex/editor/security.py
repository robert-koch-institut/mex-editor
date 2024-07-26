from secrets import compare_digest

from mex.editor.settings import EditorSettings


def has_write_access(username: str, password: str) -> bool:
    """Verify if provided credentials have write access."""
    settings = EditorSettings.get()
    write_user_db = settings.editor_user_database["write"]
    if write_user := write_user_db.get(username):
        return compare_digest(
            password.encode("ascii"), write_user.get_secret_value().encode("ascii")
        )
    return False


def has_read_access(username: str, password: str) -> bool:
    """Verify if provided credentials have read access."""
    settings = EditorSettings.get()
    read_user_db = settings.editor_user_database["read"]
    if read_user := read_user_db.get(username):
        return compare_digest(
            password.encode("ascii"), read_user.get_secret_value().encode("ascii")
        )
    return has_write_access(username, password)
