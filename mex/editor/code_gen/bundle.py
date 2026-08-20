"""Written by Claude (Anthropic).

A `Bundle` is the input to every generator: a name plus the pydantic
models that should be generated together under that name."""
from __future__ import annotations
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass(frozen=True)
class Bundle:
    """One named group of pydantic models, e.g. `Bundle("Activity",
    [ExtractedActivity, MergedActivity, ...])`. `name` becomes the output
    folder/file name (kebab-cased); `models` are the "entity types" that
    get their own generated file."""

    name: str
    models: list[type[BaseModel]]
