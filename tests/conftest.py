from typing import Any

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.settings import EditorSettings
from mex.editor.types import EditorUserDatabase, EditorUserPassword
from mex.mex import app

pytest_plugins = ("mex.common.testing.plugin",)


@pytest.fixture()
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    with TestClient(app.api, raise_server_exceptions=False) as test_client:
        return test_client


@pytest.fixture(autouse=True)
def settings() -> EditorSettings:
    return EditorSettings.get()


@pytest.fixture(autouse=True)
def patch_editor_user_database(
    is_integration_test: bool, monkeypatch: MonkeyPatch, settings: EditorSettings
) -> None:
    if not is_integration_test:
        monkeypatch.setattr(
            settings,
            "editor_user_database",
            EditorUserDatabase(
                read={"reader": EditorUserPassword("reader_pass")},
                write={"writer": EditorUserPassword("writer_pass")},
            ),
        )


@pytest.fixture()
def mocked_backend(monkeypatch: MonkeyPatch) -> None:
    def mocked_request(
        self: BackendApiConnector,
        method: str,
        endpoint: str | None = None,
        payload: Any = None,
        params: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return {
            "total": 2,
            "items": [
                {"version": 1, "name": "item-423"},
                {"version": 8, "name": "item-978"},
            ],
        }

    monkeypatch.setattr(BackendApiConnector, "request", mocked_request)
