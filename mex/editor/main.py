from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

import typer
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from reflex import constants
from reflex.config import environment, get_config
from reflex.reflex import _init, run
from reflex.state import reset_disk_state_manager
from reflex.utils.console import set_log_level
from reflex.utils.exec import get_app_module
from reflex.utils.export import export

from mex.editor.logging import UVICORN_LOGGING_CONFIG, logger
from mex.editor.settings import EditorSettings

API_DEPLOY_URL_PLACEHOLDER = "https://editor-api"
WS_DEPLOY_URL_PLACEHOLDER = "wss://editor-api"
FRONTEND_DEPLOY_URL_PLACEHOLDER = "https://editor-frontend"


def editor_api() -> None:  # pragma: no cover
    """Start the editor api."""
    settings = EditorSettings.get()

    # Set the log level.
    set_log_level(constants.LogLevel.INFO)

    # Set env mode in the environment.
    environment.REFLEX_ENV_MODE.set(constants.Env.PROD)
    environment.REFLEX_CHECK_LATEST_VERSION.set(False)

    # Skip the compile step.
    environment.REFLEX_SKIP_COMPILE.set(True)

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


def export_frontend() -> None:  # pragma: no cover
    """Export the frontend with placeholder API and deploy URLs."""
    # Set the log level.
    set_log_level(constants.LogLevel.INFO)

    # Configure the environment.
    environment.REFLEX_ENV_MODE.set(constants.Env.PROD)
    environment.REFLEX_CHECK_LATEST_VERSION.set(False)

    # Initialize the app in the current directory.
    _init(name="mex", loglevel=constants.LogLevel.INFO)

    # Export frontend as static files.
    export(
        zipping=False,
        frontend=True,
        backend=False,
        api_url=API_DEPLOY_URL_PLACEHOLDER,
        deploy_url=FRONTEND_DEPLOY_URL_PLACEHOLDER,
        loglevel=constants.LogLevel.INFO,
    )


@lru_cache(maxsize=1)
def get_frontend_headers() -> dict[str, str]:
    """Generate a dict of headers for this frontend server."""
    settings = EditorSettings.get()
    headers: dict[str, str] = {}
    websocket_server = settings.editor_api_deploy_url.replace("http", "ws", 1)
    headers["X-Content-Type-Options"] = "nosniff"
    headers["X-Frame-Options"] = "DENY"
    headers["X-XSS-Protection"] = "1; mode=block"
    headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        f"connect-src 'self' {websocket_server}"
    )
    headers["Cache-Control"] = "public, max-age=600"
    return headers


@asynccontextmanager
async def frontend_lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Replace placeholder deploy urls with actual urls from settings."""
    settings = EditorSettings.get()
    static_dir = Path(settings.editor_frontend_static_directory)
    for js_file in static_dir.glob("**/*.js"):
        content = js_file.read_text(encoding="utf-8")
        modified = False
        if API_DEPLOY_URL_PLACEHOLDER in content:
            content = content.replace(
                API_DEPLOY_URL_PLACEHOLDER, settings.editor_api_deploy_url
            )
            modified = True
        if WS_DEPLOY_URL_PLACEHOLDER in content:
            content = content.replace(
                WS_DEPLOY_URL_PLACEHOLDER,
                settings.editor_api_deploy_url.replace("http", "ws", 1),
            )
            modified = True
        if FRONTEND_DEPLOY_URL_PLACEHOLDER in content:
            content = content.replace(
                FRONTEND_DEPLOY_URL_PLACEHOLDER, settings.editor_frontend_deploy_url
            )
            modified = True
        if modified:
            js_file.write_text(content, encoding="utf-8")
            logger.info("updating deploy urls in %s", js_file.name)
    yield


def create_frontend_app() -> FastAPI:
    """Create FastAPI app for frontend with middleware."""
    app = FastAPI(lifespan=frontend_lifespan)

    @app.middleware("http")
    async def attach_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Attach security and caching headers to all responses."""
        response = await call_next(request)
        response.headers.update(get_frontend_headers())
        return response

    settings = EditorSettings.get()
    app.mount(
        "/",
        StaticFiles(
            directory=settings.editor_frontend_static_directory,
            html=True,
        ),
    )
    return app


def editor_frontend() -> None:  # pragma: no cover
    """Start the editor frontend."""
    settings = EditorSettings.get()

    # Run the frontend server
    uvicorn.run(
        "mex.editor.main:create_frontend_app",
        host=settings.editor_frontend_host,
        port=settings.editor_frontend_port,
        log_config=UVICORN_LOGGING_CONFIG,
        headers=[("server", "mex-editor")],
    )


def main() -> None:  # pragma: no cover
    """Start the editor api together with frontend."""
    environment.REFLEX_USE_NPM.set(True)
    typer.run(run)
