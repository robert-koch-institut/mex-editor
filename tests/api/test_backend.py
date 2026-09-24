from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import requests

from mex.editor.settings import EditorSettings

if TYPE_CHECKING:
    import pytest
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


def test_forwards_method_path_and_query(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_request(**kwargs: object) -> MagicMock:
        captured.update(kwargs)
        return _make_upstream()

    monkeypatch.setattr("mex.editor.api.backend.requests.request", fake_request)
    response = client.get("/api/v0/backend/merged-item", params={"limit": "5"})

    assert response.status_code == 200
    assert captured["method"] == "GET"
    settings = EditorSettings.get()
    assert captured["url"] == f"{settings.backend_api_url}v0/merged-item"
    assert ("limit", "5") in list(captured["params"])


def test_injects_api_key_and_uses_allowlist(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_request(**kwargs: object) -> MagicMock:
        captured.update(kwargs)
        return _make_upstream()

    monkeypatch.setattr("mex.editor.api.backend.requests.request", fake_request)
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

    forwarded = {k.lower(): v for k, v in captured["headers"].items()}
    settings = EditorSettings.get()
    assert forwarded["x-api-key"] == settings.backend_api_key.get_secret_value()
    assert forwarded["accept"] == "application/json"
    assert forwarded["x-forwarded-for"] == "203.0.113.7"
    assert "authorization" not in forwarded
    assert "cookie" not in forwarded
    assert "user-agent" not in forwarded


def test_forwards_non_2xx_response_verbatim(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_request(**_: object) -> MagicMock:
        return _make_upstream(status=418, content=b'{"detail":"teapot"}')

    monkeypatch.setattr("mex.editor.api.backend.requests.request", fake_request)
    response = client.get("/api/v0/backend/foo")

    assert response.status_code == 418
    assert response.json() == {"detail": "teapot"}


def test_forwards_post_body(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_request(**kwargs: object) -> MagicMock:
        captured.update(kwargs)
        return _make_upstream(status=201, content=b'{"id":"x"}')

    monkeypatch.setattr("mex.editor.api.backend.requests.request", fake_request)
    response = client.post("/api/v0/backend/rule-set", json={"title": "t"})

    assert response.status_code == 201
    assert captured["method"] == "POST"
    assert b'"title"' in captured["data"]
