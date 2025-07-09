from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mex.editor.main import (
    API_DEPLOY_URL_PLACEHOLDER,
    FRONTEND_DEPLOY_URL_PLACEHOLDER,
    WS_DEPLOY_URL_PLACEHOLDER,
    create_frontend_app,
)
from mex.editor.settings import EditorSettings


@pytest.fixture
def tmp_static_dir(tmp_path: Path) -> Path:
    static_dir = tmp_path / "static"
    static_dir.mkdir()

    # Create a dummy JS file with placeholder URLs
    (static_dir / "test-app.js").write_text(f"""
// Test js file
const API_URL = "{API_DEPLOY_URL_PLACEHOLDER}";
const FRONTEND_URL = "{FRONTEND_DEPLOY_URL_PLACEHOLDER}";
const WS_URL = "{WS_DEPLOY_URL_PLACEHOLDER}";

console.log("API URL:", API_URL);
console.log("Frontend URL:", FRONTEND_URL);
console.log("WebSocket URL:", WS_URL);
""")

    # Create an HTML file to test static serving
    (static_dir / "index.html").write_text("""
<!DOCTYPE html>
<html>
<head><title>MEx Editor</title></head>
<body><script src="/test-app.js"></script></body>
</html>
""")
    return static_dir


@pytest.fixture
def mocked_settings(tmp_static_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = EditorSettings.get()
    monkeypatch.setattr(settings, "editor_api_deploy_url", "https://api.example.com")
    monkeypatch.setattr(
        settings, "editor_frontend_deploy_url", "https://frontend.example.com"
    )
    monkeypatch.setattr(
        settings, "editor_frontend_static_directory", str(tmp_static_dir)
    )


@pytest.mark.usefixtures("mocked_settings")
def test_create_frontend_app_url_replacement(tmp_static_dir: Path) -> None:
    app = create_frontend_app()

    with TestClient(app):
        # lifespan startup should have run during context manager entry
        # check that the JS file was modified
        js_file = tmp_static_dir / "test-app.js"
        content = js_file.read_text()

        # verify placeholders were replaced with actual URLs
        assert API_DEPLOY_URL_PLACEHOLDER not in content
        assert FRONTEND_DEPLOY_URL_PLACEHOLDER not in content
        assert "https://api.example.com" in content
        assert "https://frontend.example.com" in content
        assert "wss://api.example.com" in content


@pytest.mark.usefixtures("mocked_settings")
def test_create_frontend_app_static_serving() -> None:
    app = create_frontend_app()
    with TestClient(app) as client:
        # Test HTML file serving
        response = client.get("/index.html")
        assert response.status_code == 200
        assert "MEx Editor" in response.text
        assert response.headers["content-type"] == "text/html; charset=utf-8"

        # Test JS file serving
        response = client.get("/test-app.js")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/javascript; charset=utf-8"
        assert "https://api.example.com" in response.text


@pytest.mark.usefixtures("mocked_settings")
def test_create_frontend_app_security_headers() -> None:
    app = create_frontend_app()
    with TestClient(app) as client:
        response = client.get("/index.html")
        assert response.status_code == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        expected_csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self' wss://api.example.com"
        )
        assert response.headers["Content-Security-Policy"] == expected_csp
        assert response.headers["Cache-Control"] == "public, max-age=600"


@pytest.mark.usefixtures("mocked_settings")
def test_create_frontend_app_404_handling() -> None:
    app = create_frontend_app()
    with TestClient(app) as client:
        response = client.get("/nonexistent.js")
        assert response.status_code == 404
