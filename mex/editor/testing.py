import subprocess
import sys
from typing import TYPE_CHECKING

import backoff
import requests

from mex.common.logging import logger
from mex.editor.frontend import exec_npm
from mex.editor.main import create_fastapi

if TYPE_CHECKING:
    from fastapi import FastAPI


def create_testing_api() -> FastAPI:
    """Create a FastAPI instance with only the API routes for testing."""
    return create_fastapi("api")


def create_testing_api_with_frontend() -> FastAPI:
    """Create a FastAPI instance with API routes and frontend for testing."""
    return create_fastapi("both")


@backoff.on_exception(
    backoff.constant,
    (requests.ConnectionError, requests.HTTPError),
    interval=1,
    max_tries=60,
    on_backoff=lambda details: logger.info(
        "Waiting for server (attempt %s)", details["tries"]
    ),
)
def wait_for_server() -> None:
    """Poll the api server until it responds."""
    response = requests.get("http://127.0.0.1:8000/api/v0/_system/check", timeout=5)
    response.raise_for_status()


def run() -> None:
    """Start the api server and run angular tests against it."""
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "mex.editor.testing:create_testing_api",
            "--factory",
            "--port",
            "8000",
        ],
    )
    try:
        wait_for_server()
        exec_npm(["run", "test"])
    finally:
        server.terminate()
        server.wait()
