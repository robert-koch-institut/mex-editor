"""AI-generated codegen module (Claude). Compact by design.

`Generator` base class + shared relative-import-path helper. New
generators (see zod.py) subclass `Generator` and implement `generate()`;
`run_generators()` builds the `SchemaIndex` once and hands it to every
registered generator.
"""
from __future__ import annotations
import posixpath
import re
from abc import ABC, abstractmethod
from pathlib import Path
from ..bundle import Bundle
from ..schema_collect import SchemaIndex

SUFFIX = ".ts"


class Generator(ABC):
    name: str

    @abstractmethod
    def generate(self, index: SchemaIndex, bundles: list[Bundle], output_dir: Path) -> list[Path]:
        """Write output under output_dir; return the paths written."""


def kebab(name: str) -> str:
    """PascalCase/camelCase -> kebab-case, Angular's default file-naming
    convention (ExtractedActivity -> extracted-activity)."""
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def import_specifier(from_parts: tuple[str, ...], to_parts: tuple[str, ...]) -> str:
    """Relative TS import specifier (no extension) between two files, each
    given as path segments (dirs..., filename) relative to output root."""
    from_parts, to_parts = tuple(kebab(p) for p in from_parts), tuple(kebab(p) for p in to_parts)
    from_dir = posixpath.join(*from_parts[:-1]) if len(from_parts) > 1 else "."
    to_dir = posixpath.join(*to_parts[:-1]) if len(to_parts) > 1 else "."
    rel = posixpath.relpath(to_dir, start=from_dir)
    return f"./{to_parts[-1]}" if rel == "." else f"{rel}/{to_parts[-1]}"


def write_file(output_dir: Path, file_parts: tuple[str, ...], text: str) -> Path:
    path = output_dir / Path(*(kebab(p) for p in file_parts)).with_suffix(SUFFIX)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path
