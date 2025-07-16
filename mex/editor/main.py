from pathlib import Path

import typer
import uvicorn
from reflex import constants
from reflex.config import environment, get_config
from reflex.reflex import run
from reflex.state import reset_disk_state_manager
from reflex.utils.build import setup_frontend_prod
from reflex.utils.console import set_log_level
from reflex.utils.exec import get_app_module, run_frontend_prod

from mex.editor.logging import UVICORN_LOGGING_CONFIG
from mex.editor.settings import EditorSettings


def configure_prod() -> None:
    """Configure reflex for production."""
    # Set the log level.
    set_log_level(constants.LogLevel.INFO)

    # Configure the environment.
    environment.REFLEX_ENV_MODE.set(constants.Env.PROD)
    environment.REFLEX_CHECK_LATEST_VERSION.set(False)

    # Skip the compile step.
    environment.REFLEX_SKIP_COMPILE.set(True)

    # Reload the config to make sure the env vars are persistent.
    get_config(reload=True)


def editor_api() -> None:  # pragma: no cover
    """Start the editor api.

    This function is intended as a docker entrypoint for production.
    """
    # Configure production settings
    configure_prod()

    # Delete the states folder if it exists.
    reset_disk_state_manager()

    # Run the api.
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
    # Configure production settings
    configure_prod()

    # Set up the frontend for prod mode.
    setup_frontend_prod(
        root=Path.cwd(),
        disable_telemetry=True,
    )

    # Run the frontend.
    settings = EditorSettings.get()
    run_frontend_prod(
        root=Path.cwd(),
        port=str(settings.editor_frontend_port),
        backend_present=False,
    )


def main() -> None:  # pragma: no cover
    """Start the editor api together with frontend.

    This function is intended as an entrypoint for local development.
    """
    environment.REFLEX_USE_NPM.set(True)
    typer.run(run)
