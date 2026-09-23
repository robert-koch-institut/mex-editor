import re
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from mex.editor.code_gen.models import Bundle
from mex.editor.code_gen.zod_generator import generate_zod_schemas, kebab

if TYPE_CHECKING:
    from pydantic import BaseModel

EXT = ".ts"


def generate(models: list[type[BaseModel]]) -> dict[str, str]:
    """Generate one bundle named `Thing` and return its files by name."""
    output_dir = Path(tempfile.mkdtemp(prefix="code_gen_"))
    written = generate_zod_schemas([Bundle(name="Thing", models=models)], output_dir)
    return {p.name: p.read_text() for p in written}


def bundle_file(out_dir: Path, bundle: str) -> Path:
    """The generated file for `bundle`."""
    return out_dir / f"{kebab(bundle)}{EXT}"


def shared_file(out_dir: Path) -> Path:
    """The generated file holding defs used by more than one bundle."""
    return out_dir / f"shared{EXT}"


def brackets_balanced(text: str) -> bool:
    """Check that braces and parens in `text` pair up."""
    return text.count("{") == text.count("}") and text.count("(") == text.count(")")


def declaration_order_ok(text: str) -> bool:
    """Check that no declaration is referenced before it is declared.

    No `const`/`type` is referenced (outside its own declaration line
    or its doc comment) before it's declared -- const isn't hoisted in
    JS, so a forward reference throws at runtime, not just a lint issue.
    """
    lines = text.splitlines()
    declared_at: dict[str, int] = {}
    for i, line in enumerate(lines):
        m = re.match(r"export (?:const|type) (\w+)", line)
        if m:
            declared_at[m.group(1)] = i
    code_lines = [
        (i, re.sub(r'"(?:[^"\\]|\\.)*"', '""', line))
        for i, line in enumerate(lines)
        if not re.match(r"\s*(/\*\*|\*|\*/)", line)
    ]
    for name, at in declared_at.items():
        for i, line in code_lines:
            if i != at and re.search(rf"\b{re.escape(name)}\b", line) and i < at:
                return False
    return True
