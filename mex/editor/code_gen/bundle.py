from __future__ import annotations
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass(frozen=True)
class Bundle:
    name: str
    models: list[type[BaseModel]]
