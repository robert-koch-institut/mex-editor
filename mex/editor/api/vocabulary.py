from fastapi import APIRouter, HTTPException
from starlette import status

from mex.common.models import PaginatedItemsContainer
from mex.common.types import VOCABULARY_ENUMS_BY_NAME
from mex.common.types.vocabulary import Concept

router = APIRouter()

_VOCABULARIES_BY_SLUG = {
    enum.__vocabulary__: enum for enum in VOCABULARY_ENUMS_BY_NAME.values()
}


@router.get(
    "/vocabulary",
    tags=["vocabulary"],
)
def list_vocabularies() -> list[str]:
    """List the names of all available vocabularies."""
    return sorted(_VOCABULARIES_BY_SLUG)


@router.get(
    "/vocabulary/{name}",
    tags=["vocabulary"],
)
def get_vocabulary(name: str) -> PaginatedItemsContainer[Concept]:
    """Get the concepts of a single vocabulary by its name."""
    if (enum := _VOCABULARIES_BY_SLUG.get(name)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown vocabulary: {name}",
        )
    concepts = enum.__concepts__
    return PaginatedItemsContainer[Concept](items=concepts, total=len(concepts))
