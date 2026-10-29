from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from starlette import status

from mex.editor.main import create_fastapi
from mex.editor.middleware import APP_CSP, DOCS_CSP, SECURITY_HEADERS

if TYPE_CHECKING:
    from pytest import MonkeyPatch

    from mex.editor.settings import EditorSettings


@pytest.mark.parametrize(
    ("path", "expected_csp", "expected_cache_control"),
    [
        ("/api/v0/_system/check", APP_CSP, "no-store"),
        ("/docs", DOCS_CSP, "no-cache"),
    ],
    ids=["api", "docs"],
)
def test_security_headers(
    client: TestClient, path: str, expected_csp: str, expected_cache_control: str
) -> None:
    response = client.get(path)

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.headers["Content-Security-Policy"] == expected_csp
    assert response.headers["Cache-Control"] == expected_cache_control
    for name, value in SECURITY_HEADERS.items():
        assert response.headers[name] == value


def test_redoc_is_disabled(client: TestClient) -> None:
    response = client.get("/redoc")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    ("allowed_origins", "expected_header"),
    [([], None), (["https://admin.example.org"], "https://admin.example.org")],
    ids=["same-origin-only", "configured-origin"],
)
def test_cors_allowed_origins(
    monkeypatch: MonkeyPatch,
    settings: EditorSettings,
    allowed_origins: list[str],
    expected_header: str | None,
) -> None:
    monkeypatch.setattr(settings, "cors_allowed_origins", allowed_origins)

    with TestClient(create_fastapi("api")) as client:
        response = client.get(
            "/api/v0/_system/check", headers={"Origin": "https://admin.example.org"}
        )

    assert response.headers.get("Access-Control-Allow-Origin") == expected_header


def test_cors_preflight_restricts_methods_and_headers(
    monkeypatch: MonkeyPatch, settings: EditorSettings
) -> None:
    monkeypatch.setattr(settings, "cors_allowed_origins", ["https://admin.example.org"])
    preflight = {
        "Origin": "https://admin.example.org",
        "Access-Control-Request-Method": "POST",
    }

    with TestClient(create_fastapi("api")) as client:
        allowed = client.options(
            "/api/v0/_system/check",
            headers={**preflight, "Access-Control-Request-Headers": "content-type"},
        )
        disallowed = client.options(
            "/api/v0/_system/check",
            headers={**preflight, "Access-Control-Request-Headers": "x-api-key"},
        )

    assert allowed.status_code == 200
    assert "*" not in allowed.headers["Access-Control-Allow-Methods"]
    assert disallowed.status_code == 400
