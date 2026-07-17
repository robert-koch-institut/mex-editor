from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Literal

import click
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.datastructures import Headers
from starlette.exceptions import HTTPException as StarletteHTTPException

from mex.common.logging import logger
from mex.editor.api.backend import router as backend_router
from mex.editor.api.i18n import router as i18n_router
from mex.editor.api.system import router as system_router
from mex.editor.api.vocabulary import router as vocabulary_router
from mex.editor.frontend import STATIC_DIR, npm_watch
from mex.editor.logging import UVICORN_LOGGING_CONFIG
from mex.editor.settings import EditorSettings

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import AsyncGenerator

    from starlette.responses import Response
    from starlette.types import Scope


class SPAStaticFiles(StaticFiles):
    """Custom implementation of StaticFiles for Single Page Applications (SPA)."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        """Try to serve the file at 'path', or fall back to 'index.html' for SPA.

        This allows browser-based navigation to work correctly.
        """
        try:
            return await super().get_response(path, scope)
        except (HTTPException, StarletteHTTPException) as error:
            if error.status_code != status.HTTP_404_NOT_FOUND:
                raise
            # Only fall back to index.html for SPA navigation requests
            # (i.e. browsers asking for HTML). Asset requests get a real 404.
            if "text/html" not in Headers(scope=scope).get("accept", ""):
                raise
            return await super().get_response("index.html", scope)


API_PREFIX = "/api/v0"


@asynccontextmanager
async def dev_lifespan(_: FastAPI) -> AsyncGenerator[None]:  # pragma: no cover
    """Run npm watch during dev mode."""
    logger.info("Starting npm run watch")
    with npm_watch():
        yield
    logger.info("Stopped npm run watch")


def create_fastapi(
    startup: Literal["api", "frontend", "both"] = "both",
    mode: Literal["dev"] | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = EditorSettings.get()
    app = FastAPI(
        title="mex-editor-ng",
        lifespan=dev_lifespan if mode == "dev" else None,
        root_path="" if settings.base_href == "/" else settings.base_href.rstrip("/"),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if startup in ["api", "both"]:
        app.include_router(backend_router, prefix=API_PREFIX)
        app.include_router(system_router, prefix=API_PREFIX)
        app.include_router(i18n_router, prefix=API_PREFIX)
        app.include_router(vocabulary_router, prefix=API_PREFIX)
    if startup in ["frontend", "both"]:
        app.mount(
            "/",
            SPAStaticFiles(directory=STATIC_DIR, html=True),
            name="spa-static-files",
        )
    return app


@click.command()
@click.option(
    "--startup",
    type=click.Choice(["api", "frontend", "both"]),
    default="both",
    help="Define what should start 'api', 'frontend' or 'both'.",
)
@click.option(
    "--dev",
    "-d",
    is_flag=True,
    default=False,
    help="Define if started in dev mode to watch angular src and rebuild on change.",
)
def main(
    *,
    startup: Literal["api", "frontend", "both"] = "both",
    dev: bool = False,
) -> None:  # pragma: no cover
    """Start the mex-editor-ng api."""
    settings = EditorSettings.get()
    app = create_fastapi(startup, "dev" if dev else None)
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        root_path="" if settings.base_href == "/" else settings.base_href.rstrip("/"),
        log_config=UVICORN_LOGGING_CONFIG,
        headers=[("server", "mex-editor-ng")],
    )


if __name__ == "__main__":  # pragma: no cover
    main()
