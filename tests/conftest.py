import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from pytest import MonkeyPatch

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
def reader_user_credentials() -> tuple[str, SecretStr]:
    settings = EditorSettings.get()
    for username, password in settings.editor_user_database["read"].items():
        return username, password
    raise RuntimeError("No reader configured")  # pragma: no cover


@pytest.fixture()
def writer_user_credentials() -> tuple[str, SecretStr]:
    settings = EditorSettings.get()
    for username, password in settings.editor_user_database["write"].items():
        return username, password
    raise RuntimeError("No writer configured")  # pragma: no cover
