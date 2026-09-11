import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from mex.common.models import (
    ActivityRuleSetResponse,
    ExtractedActivity,
    ExtractedResource,
    MergedActivity,
    MergedResource,
    ResourceRuleSetResponse,
)
from mex.editor.code_gen.models import Bundle

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(scope="session")
def bundles() -> list[Bundle]:
    """Two bundles of the real mex-common models, not synthetic stand-ins."""
    return [
        Bundle(
            name="Activity",
            models=[ExtractedActivity, MergedActivity, ActivityRuleSetResponse],
        ),
        Bundle(
            name="Resource",
            models=[ExtractedResource, MergedResource, ResourceRuleSetResponse],
        ),
    ]


@pytest.fixture
def out_dir() -> Generator[Path, Any]:
    """A throwaway directory to generate into."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)
