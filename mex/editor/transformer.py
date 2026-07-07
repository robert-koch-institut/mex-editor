from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import polib


class DuplicateKeyError(KeyError):
    """Exception raised when a duplicate key created during pofile transformation."""

    def __init__(
        self,
        key: str,
        entry: polib.POEntry,
        message: str = "Key already exists and duplicates are not allowed",
    ) -> None:
        """Initialize DuplicateKeyError.

        Args:
            key (str): The duplicated key.
            entry (polib.POEntry): The entry for which the key was generated.
            message (str, optional): Defaults to "Key already exists and
            duplicates are not allowed".
        """
        self.key = key
        self.message = f"{message}: '{key} (linenum: {entry.linenum})"
        super().__init__(self.message)


def transform_pofile_to_message_format_json(
    po: polib.POFile | list[polib.POEntry],
) -> dict[str, str]:
    """Transforms the given pofile (or entries) to message format json.

    Args:
        po (polib.POFile | list[polib.POEntry]): input to transform.

    Raises:
        DuplicateKeyError: Raises if the key generation creates a duplicate key.

    Returns:
        dict[str, str]: Returns the entries in message format.
    """
    messages = {}
    for entry in po:
        if not entry.msgid:
            continue
        if entry.msgid_plural:
            key = (
                entry.msgid_plural.replace(".plural", "")
                if not entry.msgctxt
                else f"{entry.msgctxt}.{entry.msgid_plural.replace('.plural', '')}"
            )
            value = f"{{count, plural, one {{{entry.msgstr_plural[0]}}} other {{{entry.msgstr_plural[1]}}}}}"  # noqa: E501
        else:
            key = (
                entry.msgid.replace(".singular", "")
                if not entry.msgctxt
                else f"{entry.msgctxt}.{entry.msgid.replace('.singular', '')}"
            )
            value = entry.msgstr

        if key in messages:
            raise DuplicateKeyError(key, entry)

        messages[key] = value

    return messages
