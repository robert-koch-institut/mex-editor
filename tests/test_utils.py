import nest_asyncio
import pytest

from mex.common.exceptions import EmptySearchResultError, MExError
from mex.common.models import AnyExtractedModel, ExtractedPrimarySource
from mex.editor.models import EditorValue
from mex.editor.utils import resolve_editor_value, resolve_identifier

nest_asyncio.apply()


@pytest.fixture
def anyio_backend():
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
        text=dummy_primary_source.stableTargetId,
        is_identifier=True,
        resolved=False,
    )
    expected = EditorValue(
        text=dummy_primary_source.stableTargetId,
        display_text=dummy_primary_source.title[0].value,
        is_identifier=True,
        resolved=True,
    )
    await resolve_editor_value(editor_value)
    assert editor_value == expected

    with pytest.raises(MExError):
        await resolve_editor_value(EditorValue(is_identifier=False))
