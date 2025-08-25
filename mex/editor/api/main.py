from importlib.metadata import version

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from mex.common.connector import CONNECTOR_STORE
from mex.editor.api.models import SystemStatus

api = FastAPI(
    title="mex-editor",
    version="v0",
    contact={"name": "MEx Team", "email": "mex@rki.de"},
    description="Metadata editor web application.",
)


@api.get("/_system/check", tags=["system"])
def check_system_status() -> SystemStatus:
    """Check that the editor server is healthy and responsive."""
    return SystemStatus(status="ok", version=version("mex-editor"))


@api.get("/_system/metrics", response_class=PlainTextResponse, tags=["system"])
def get_prometheus_metrics() -> str:
    """Get connector metrics for prometheus."""
    return "\n\n".join(
        f"# TYPE {key} counter\n{key} {value}"
        for key, value in CONNECTOR_STORE.metrics().items()
    )
