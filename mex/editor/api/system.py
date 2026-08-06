from importlib.metadata import version

from fastapi import APIRouter

from mex.common.models import VersionStatus

router = APIRouter()


@router.get(
    "/_system/check",
    tags=["system"],
)
def check_system_status() -> VersionStatus:
    """Check that the server is healthy and responsive."""
    return VersionStatus(status="ok", version=version("mex-editor"))
