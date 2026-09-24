import logging
from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from pytest import LogCaptureFixture

from mex.common.logging import logger
from mex.editor.settings import EditorSettings
from mex.editor.testing import create_testing_api, create_testing_api_with_frontend

if TYPE_CHECKING:
    from collections.abc import Generator

pytest_plugins = ("mex.common.testing.plugin",)


@pytest.fixture(autouse=True)
def settings(
    caplog: LogCaptureFixture,
    request: pytest.FixtureRequest,
    isolate_settings: None,  # noqa: ARG001
) -> EditorSettings:
    """Load and return the correct editor settings."""
    verbosity = request.config.option.verbose
    cutoff_level = logging.INFO if verbosity >= 2 else logging.WARNING
    with caplog.at_level(cutoff_level, logger=logger.name):
        return EditorSettings.get()


@pytest.fixture(scope="session")
def client() -> Generator[TestClient]:
    """Return a fastAPI test client initialized with our app."""
    app = create_testing_api()
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def client_with_frontend() -> Generator[TestClient]:
    """Return a fastAPI test client initialized with API and frontend."""
    app = create_testing_api_with_frontend()
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
