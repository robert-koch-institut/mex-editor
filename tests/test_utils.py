import nest_asyncio
import pytest

from mex.common.models import AnyExtractedModel, ExtractedPrimarySource
from mex.editor.utils import resolve_identifier

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
