from functools import lru_cache
from importlib.resources import files
from typing import TYPE_CHECKING, Literal, cast

import polib
from fastapi import APIRouter

from mex.editor.transformer import transform_pofile_to_message_format_json

if TYPE_CHECKING:
    from pathlib import Path

model_locale_path = cast("Path", (files("mex.model") / "i18n"))
router = APIRouter()


@router.api_route(
    "/i18n/{lang}",
)
@lru_cache(maxsize=2)
def get_mex_model_translations(lang: Literal["de", "en"]) -> dict[str, str]:
    """Convert mex model .po files to .json files."""
    po = polib.pofile(model_locale_path / f"{lang}.po")
    return transform_pofile_to_message_format_json(po)
