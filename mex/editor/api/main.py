from importlib.metadata import version

from pydantic import BaseModel


class SystemStatus(BaseModel):
    """Response model for system status check."""

    status: str
    version: str


def check_system_status() -> SystemStatus:
    """Check that the editor server is healthy and responsive."""
    return SystemStatus(status="ok", version=version("mex-editor"))
