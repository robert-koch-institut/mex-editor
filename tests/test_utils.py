import re

import nest_asyncio  # type: ignore[import-untyped]
import pytest

from mex.common.exceptions import EmptySearchResultError, MExError
from mex.common.models import AnyExtractedModel, ExtractedPrimarySource
from mex.editor.locale_service import LocaleService
from mex.editor.models import EditorValue
from mex.editor.utils import resolve_editor_value, resolve_identifier

nest_asyncio.apply()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
@pytest.mark.anyio
async def test_resolve_identifier(
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    dummy_primary_source = dummy_data_by_identifier_in_primary_source["ps-1"]
    assert isinstance(dummy_primary_source, ExtractedPrimarySource)
    returned = await resolve_identifier(dummy_primary_source.stableTargetId)
    assert returned == dummy_primary_source.title[0].value

    with pytest.raises(EmptySearchResultError):
        await resolve_identifier("IdentifierDoesNotExist")


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
@pytest.mark.anyio
async def test_resolve_editor_value(
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> None:
    dummy_primary_source = dummy_data_by_identifier_in_primary_source["ps-1"]
    assert isinstance(dummy_primary_source, ExtractedPrimarySource)
    editor_value = EditorValue(
        identifier=dummy_primary_source.stableTargetId,
    )
    expected = EditorValue(
        identifier=dummy_primary_source.stableTargetId,
        text=dummy_primary_source.title[0].value,
    )
    await resolve_editor_value(editor_value)
    assert editor_value == expected

    with pytest.raises(MExError):
        await resolve_editor_value(EditorValue(identifier=None))


def build_pagination_regex(current: int, total: int) -> re.Pattern:
    return re.compile(rf"\w+\s{current}\s\w+\s{total}\s\w+")


def build_ui_label_regex(label_id: str) -> re.Pattern:
    service = LocaleService.get()
    return re.compile(
        f"({'|'.join(re.escape(service.get_ui_label(locale.id, label_id)) for locale in service.get_available_locales())})"
    )
