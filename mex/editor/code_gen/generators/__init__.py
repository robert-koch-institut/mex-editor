"""AI-generated codegen module (Claude). Compact by design.

Generator registry: base class + the built-in generators.
"""
from __future__ import annotations
from pathlib import Path
from ..bundle import Bundle
from ..schema_collect import build_schema_index
from .base import Generator, import_specifier
from .interfaces import TypeScriptInterfaceGenerator
from .validators import AngularSignalFormValidatorGenerator
from .zod import ZodSchemaGenerator

__all__ = [
    "AngularSignalFormValidatorGenerator",
    "Generator",
    "TypeScriptInterfaceGenerator",
    "ZodSchemaGenerator",
    "import_specifier",
    "run_generators",
]


def run_generators(bundles: list[Bundle], output_dir: str | Path, generators: list[Generator]) -> list[Path]:
    """Build the SchemaIndex once, hand it to every generator."""
    output_dir = Path(output_dir)
    index = build_schema_index(bundles)
    return [p for g in generators for p in g.generate(index, bundles, output_dir)]
