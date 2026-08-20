#!/usr/bin/env python3

import logging
import re
import sys
from pathlib import Path

# Named argument indexes to avoid magic numbers (PLR2004)
INPUT_ARG_INDEX = 1
OUTPUT_ARG_INDEX = 2


def main(argv: list[str]) -> int:
    """Convert a theme CSS file to the format used by the editor."""
    logger = logging.getLogger(__name__)
    input_path = (
        Path(argv[INPUT_ARG_INDEX])
        if len(argv) > INPUT_ARG_INDEX
        else Path("theme-export/light.css")
    )
    output_path = (
        Path(argv[OUTPUT_ARG_INDEX])
        if len(argv) > OUTPUT_ARG_INDEX
        else Path("src/theme-tokens.css")
    )

    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        logger.error("Usage: python scripts/import-theme.py <input.css> <output.css>")
        return 1

    text = input_path.read_text(encoding="utf-8")

    # Replace variable prefix
    text = re.sub(r"--md-sys-color-([a-z0-9-]+):", r"--mat-sys-\1:", text)

    # Replace the top selector (whatever it is) with :root {
    text = re.sub(r"^[^{]+\{", ":root {", text, count=1, flags=re.DOTALL)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")

    logger.info("Wrote %s from %s", output_path, input_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
