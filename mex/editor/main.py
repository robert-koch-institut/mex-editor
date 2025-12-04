import os
import sys
from pathlib import Path

import uvicorn
from reflex import constants
from reflex.config import environment, get_config
from reflex.reflex import _init, run
from reflex.state import reset_disk_state_manager
from reflex.utils.build import setup_frontend_prod
from reflex.utils.console import set_log_level
from reflex.utils.exec import get_app_module, run_frontend_prod
from reflex.utils.prerequisites import get_compiled_app

from mex.editor.logging import UVICORN_LOGGING_CONFIG
from mex.editor.settings import EditorSettings


def editor_api() -> None:  # pragma: no cover
    """Start the editor api."""
    settings = EditorSettings.get()

    # Set the log level.
    set_log_level(constants.LogLevel.INFO)

    # Set environment variables.
    environment.REFLEX_ENV_MODE.set(constants.Env.PROD)
    environment.REFLEX_SKIP_COMPILE.set(True)
    environment.REFLEX_USE_GRANIAN.set(False)

    # Delete the states folder if it exists.
    reset_disk_state_manager()

    # Reload the config to make sure the env vars are persistent.
    get_config(reload=True)

    # Run the api.
    uvicorn.run(
        get_app_module(),
        host=settings.editor_api_host,
        port=settings.editor_api_port,
        root_path=settings.editor_api_root_path,
        log_config=UVICORN_LOGGING_CONFIG,
        headers=[("server", "mex-editor")],
    )


def editor_frontend() -> None:  # pragma: no cover
    """Start the editor frontend."""
    settings = EditorSettings.get()

    # Set the log level.
    set_log_level(constants.LogLevel.INFO)

    # Configure the environment.
    environment.REFLEX_ENV_MODE.set(constants.Env.PROD)
    environment.REFLEX_CHECK_LATEST_VERSION.set(False)

    # Initialize the app in the current directory.
    _init(name="mex")

    # Get the app module.
    get_compiled_app()

    # Set up the frontend for prod mode.
    setup_frontend_prod(
        Path.cwd(),
        disable_telemetry=True,
    )

    # Run the frontend.
    run_frontend_prod(
        Path.cwd(),
        str(settings.editor_frontend_port),
        backend_present=False,
    )


def main() -> None:  # pragma: no cover
    """Start the editor api together with frontend."""
    # Set environment variables.
    environment.REFLEX_USE_GRANIAN.set(False)

    if "win32" in sys.platform:
        # bun cache is not working correctly on windows
        # https://github.com/oven-sh/bun/issues/20886
        os.environ["BUN_OPTIONS"] = "--no-cache"

    # Run the editor.
    run.main()
