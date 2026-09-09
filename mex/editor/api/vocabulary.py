from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette import status

from mex.model import VOCABULARY_JSON_BY_NAME

router = APIRouter()


class BilingualText(BaseModel):
    """String-field translated in German and English."""

    de: str | None = None
    en: str | None = None


class Concept(BaseModel):
    """Single entry in a vocabulary with a stable identifier and labels."""

    identifier: str
    prefLabel: BilingualText
    altLabel: list[BilingualText] = []


_CONCEPTS_BY_SLUG = {
    name.replace("_", "-"): [Concept.model_validate(concept) for concept in concepts]
    for name, concepts in VOCABULARY_JSON_BY_NAME.items()
}


@router.get(
    "/vocabulary/{name}",
    tags=["vocabulary"],
)
def get_vocabulary(name: str) -> list[Concept]:
    """Get the concepts of a single vocabulary by its name."""
    if (concepts := _CONCEPTS_BY_SLUG.get(name)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown vocabulary: {name}",
        )
    return concepts
