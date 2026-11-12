from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastapi import FastAPI, Request, Response

SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "DENY",
}
# angular material injects component styles at runtime, hence 'unsafe-inline' styles
APP_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "object-src 'none'"
)
# the swagger ui loads its js and css from jsdelivr and runs one inline script
DOCS_CSP = (
    "default-src 'none'; "
    "script-src https://cdn.jsdelivr.net 'unsafe-inline'; "
    "style-src https://cdn.jsdelivr.net; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'"
)
DOCS_PATHS = ("/docs", "/docs/oauth2-redirect")


def add_security_headers(app: FastAPI, api_prefix: str) -> None:
    """Set security headers on every http response of the given app.

    API responses may contain personal data and are never cached, frontend
    assets may be cached but must be revalidated.
    """

    @app.middleware("http")
    async def set_security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        path = request.url.path
        response.headers.update(SECURITY_HEADERS)
        response.headers["Content-Security-Policy"] = (
            DOCS_CSP if path.endswith(DOCS_PATHS) else APP_CSP
        )
        response.headers.setdefault(
            "Cache-Control", "no-store" if f"{api_prefix}/" in path else "no-cache"
        )
        return response
