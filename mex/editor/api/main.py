from importlib.metadata import version

from mex.common.connector import CONNECTOR_STORE
from mex.editor.api.models import SystemStatus


def check_system_status() -> SystemStatus:
    """Check that the editor server is healthy and responsive."""
    return SystemStatus(status="ok", version=version("mex-editor"))


def get_prometheus_metrics() -> str:
    """Get connector metrics for prometheus."""
    return "\n\n".join(
        f"# TYPE {key} counter\n{key} {value}"
        for key, value in CONNECTOR_STORE.metrics().items()
    )
