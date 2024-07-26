from pydantic import BaseModel


class SystemStatus(BaseModel):
    """Response model for system status check."""

    status: str


def check_system_status() -> SystemStatus:
    """Check that the backend server is healthy and responsive."""
    return SystemStatus(status="ok")
