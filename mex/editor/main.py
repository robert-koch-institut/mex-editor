import typer
import uvicorn
from reflex.config import environment
from reflex.reflex import run
from reflex.utils.build import setup_frontend_prod
from reflex.utils.exec import get_app_module, run_frontend_prod

from mex.editor.logging import UVICORN_LOGGING_CONFIG
from mex.editor.settings import EditorSettings


def editor_api() -> None:  # pragma: no cover
    """Start the editor api.

    This function is intended as a docker entrypoint for production.
    """
    settings = EditorSettings.get()
    uvicorn.run(
        get_app_module(),
        host=settings.editor_api_host,
        port=settings.editor_api_port,
        root_path=settings.editor_api_root_path,
        log_config=UVICORN_LOGGING_CONFIG,
        headers=[("server", "mex-editor")],
    )


def editor_frontend() -> None:  # pragma: no cover
    """Start the editor frontend.

    This function is intended as a docker entrypoint for production.
    """
    settings = EditorSettings.get()
    setup_frontend_prod(
        root=settings.work_dir,
        disable_telemetry=True,
    )
    run_frontend_prod(
        root=settings.work_dir,
        port=str(settings.editor_frontend_port),
        backend_present=False,
    )


def main() -> None:  # pragma: no cover
    """Start the editor api together with frontend.

    This function is intended as an entrypoint for local development.
    """
    environment.REFLEX_USE_NPM.set(True)
    typer.run(run)
