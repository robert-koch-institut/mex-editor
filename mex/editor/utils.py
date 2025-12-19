from async_lru import alru_cache

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.exceptions import EmptySearchResultError, MExError
from mex.common.settings import SETTINGS_STORE
from mex.editor.models import EditorValue
from mex.editor.settings import EditorSettings
from mex.editor.transform import transform_models_to_title


@alru_cache(maxsize=5000)
async def resolve_identifier(identifier: str) -> str:
    """Resolve identifiers to human readable display values."""
    # TODO(ND): use proper connector method when available (stop-gap MX-1984)
    connector = BackendApiConnector.get()
    response = connector.fetch_preview_items(identifier=identifier, limit=1)
    if len(response.items) != 1:
        msg = f"No item found for identifier '{identifier}'"
        raise EmptySearchResultError(msg)
    title = transform_models_to_title(response.items)[0]
    return f"{title.text}"


async def resolve_editor_value(editor_value: EditorValue) -> None:
    """Resolve editor text values to human readable display values."""
    if editor_value.identifier:
        editor_value.text = await resolve_identifier(editor_value.identifier)
    else:
        msg = f"Cannot resolve editor value: {editor_value}"
        raise MExError(msg)


def load_settings() -> EditorSettings:
    """Reset the settings store and fetch the editor settings."""
    SETTINGS_STORE.reset()
    return EditorSettings.get()


TCompareSeq = TypeVar("TCompareSeq")


def compare_sequences(
    left: Sequence[TCompareSeq],
    right: Sequence[TCompareSeq],
    key: Callable[[TCompareSeq], Any] | None,
    comparator: Callable[[TCompareSeq, TCompareSeq], bool],
) -> bool:
    """Compare two sequences by a given key and comperator.

    How it works:
    1. Sort sequences by key (if key provided)
    2. Check if sequences have same length
    3. Compare all items by index
        a. Compare if the keys are equal (if key provided)
        b. Compare items by given comperator

    Args:
        left (Sequence[TCompareSeq]): Left sequence to compare.
        right (Sequence[TCompareSeq]): Right sequence to compare
        key (Callable[[TCompareSeq], Any] | None): Key to sort sequences and compare
        items.
        comparator (Callable[[TCompareSeq, TCompareSeq], bool]): Comperator to use for
        check comparison of items.

    Returns:
        True if the sequences are equal; otherwise False.
    """
    if key:
        left = sorted(left, key=key)
        right = sorted(right, key=key)
    left_len = len(left)
    if left_len != len(right):
        return False

    for i in range(left_len):
        left_item = left[i]
        right_item = right[i]
        if key and key(left_item) != key(right_item):
            return False
        if not comparator(left_item, right_item):
            return False

    return True
