import typer
from reflex.reflex import run


def main() -> None:  # pragma: no cover
    """Start the editor service."""
    typer.run(run)
