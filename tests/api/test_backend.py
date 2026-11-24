from typing import TYPE_CHECKING, Any, cast
from unittest.mock import MagicMock

import pytest
import requests

from mex.common.backend_api.connector import BackendApiConnector
from mex.editor.settings import EditorSettings

if TYPE_CHECKING:
    from pathlib import Path

    from fastapi.testclient import TestClient


def _make_upstream(
    *,
    status: int = 200,
    content: bytes = b'{"ok":true}',
    content_type: str = "application/json",
) -> MagicMock:
    upstream = MagicMock(spec=requests.Response)
    upstream.status_code = status
    upstream.content = content
    upstream.headers = {"content-type": content_type}
    return upstream


@pytest.fixture(autouse=True)
def session(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Replace the backend connector with a fake that has a mocked session."""
    connector = MagicMock(spec=BackendApiConnector)
    connector.url = f"{EditorSettings.get().backend_api_url}v0"
    connector.session = MagicMock(spec=requests.Session)
    connector.session.request.return_value = _make_upstream()
    monkeypatch.setattr(BackendApiConnector, "get", lambda: connector)
    return cast("MagicMock", connector.session)


def _captured(session: MagicMock) -> dict[str, Any]:
    session.request.assert_called_once()
    return cast("dict[str, Any]", session.request.call_args.kwargs)


def test_forwards_method_path_and_query(client: TestClient, session: MagicMock) -> None:
    response = client.get("/api/v0/backend/merged-item", params={"limit": "5"})

    assert response.status_code == 200
    captured = _captured(session)
    assert captured["method"] == "GET"
    settings = EditorSettings.get()
    assert captured["url"] == f"{settings.backend_api_url}v0/merged-item"
    assert ("limit", "5") in list(captured["params"])


def test_uses_header_allowlist(client: TestClient, session: MagicMock) -> None:
    client.get(
        "/api/v0/backend/anything",
        headers={
            "X-API-Key": "sneaky-client-key",
            "Authorization": "Bearer sneaky",
            "Cookie": "session=abc",
            "Accept": "application/json",
            "X-Forwarded-For": "203.0.113.7",
        },
    )

    forwarded = {k.lower(): v for k, v in _captured(session)["headers"].items()}
    assert forwarded["accept"] == "application/json"
    assert forwarded["x-forwarded-for"] == "203.0.113.7"
    # the editor's API key is set on the connector session, not per request
    assert "x-api-key" not in forwarded
    assert "authorization" not in forwarded
    assert "cookie" not in forwarded
    assert "user-agent" not in forwarded


def test_forwards_non_2xx_response_verbatim(
    client: TestClient, session: MagicMock
) -> None:
    session.request.return_value = _make_upstream(
        status=418, content=b'{"detail":"teapot"}'
    )
    response = client.get("/api/v0/backend/foo")

    assert response.status_code == 418
    assert response.json() == {"detail": "teapot"}


def test_forwards_post_body(client: TestClient, session: MagicMock) -> None:
    session.request.return_value = _make_upstream(status=201, content=b'{"id":"x"}')
    response = client.post("/api/v0/backend/rule-set", json={"title": "t"})

    assert response.status_code == 201
    captured = _captured(session)
    assert captured["method"] == "POST"
    assert b'"title"' in captured["data"]


def test_logs_warning_on_5xx_response(
    client: TestClient, session: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    session.request.return_value = _make_upstream(
        status=502, content=b'{"detail":"bad gateway"}'
    )
    mock_warning = MagicMock()
    monkeypatch.setattr("mex.editor.api.backend.logger.warning", mock_warning)
    response = client.get("/api/v0/backend/foo")

    assert response.status_code == 502
    assert response.json() == {"detail": "bad gateway"}
    mock_warning.assert_called_once()
    _, method, url, status_code = mock_warning.call_args.args
    assert method == "GET"
    assert url.endswith("v0/foo")
    assert status_code == 502


def test_connector_session_uses_api_key_and_verify_setting(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    settings = EditorSettings.get()
    ca_bundle = tmp_path / "ca.pem"
    monkeypatch.setattr(settings, "verify_session", ca_bundle)
    monkeypatch.setattr(BackendApiConnector, "_check_availability", lambda _: None)

    connector = BackendApiConnector()

    assert connector.session.verify == ca_bundle  # type: ignore[comparison-overlap]
    assert (
        connector.session.headers["X-API-Key"]
        == settings.backend_api_key.get_secret_value()
    )
    connector.close()
