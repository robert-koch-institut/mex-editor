def render(value: object) -> str:
    """Simple rendering function to stringify objects."""
    if isinstance(value, dict):
        return ", ".join(f"{k}: {render(v)}" for k, v in value.items() if v)
    if isinstance(value, list):
        return ", ".join(render(v) for v in value)
    return str(value) if value else ""
