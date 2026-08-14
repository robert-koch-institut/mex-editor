"""AI-generated codegen package (Claude). Kept compact -- the *generated*
TypeScript should be readable, this Python doesn't need to be.

    from mex_form_codegen import Bundle, generate_typescript_interfaces, generate_angular_signal_form_validators
    bundles = [Bundle(name="Activity", models=[ExtractedActivity, MergedActivity])]
    generate_typescript_interfaces(bundles, "out")
    generate_angular_signal_form_validators(bundles, "out")

To add a new generator (see generators/zod.py for a full example):
subclass Generator, implement generate(index, bundles, output_dir), then
run_generators(bundles, "out", [TypeScriptInterfaceGenerator(), YourGenerator()]).
See README.md.
"""
from __future__ import annotations
from pathlib import Path
from .bundle import Bundle
from .generators import (
    AngularSignalFormValidatorGenerator,
    Generator,
    TypeScriptInterfaceGenerator,
    ZodSchemaGenerator,
    run_generators,
)

__all__ = [
    "AngularSignalFormValidatorGenerator",
    "Bundle",
    "Generator",
    "TypeScriptInterfaceGenerator",
    "ZodSchemaGenerator",
    "generate_angular_signal_form_validators",
    "generate_typescript_interfaces",
    "run_generators",
]


def generate_typescript_interfaces(bundles: list[Bundle], output_dir: str | Path) -> list[Path]:
    return run_generators(bundles, output_dir, [TypeScriptInterfaceGenerator()])


def generate_angular_signal_form_validators(bundles: list[Bundle], output_dir: str | Path) -> list[Path]:
    return run_generators(bundles, output_dir, [AngularSignalFormValidatorGenerator()])
