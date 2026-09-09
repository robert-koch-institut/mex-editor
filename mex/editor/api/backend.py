from functools import partial
from urllib.parse import urljoin

import requests
from fastapi import APIRouter, Request, Response
from starlette import status
from starlette.concurrency import run_in_threadpool

from mex.common.logging import logger
from mex.editor.settings import EditorSettings

router = APIRouter()

_FORWARD_REQUEST = frozenset({"content-type", "accept", "x-forwarded-for"})
_STRIP_RESPONSE = frozenset({"content-length", "transfer-encoding", "connection"})


@router.api_route(
    "/backend/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def backend_proxy(path: str, request: Request) -> Response:
    """Forward a request to the mex-backend with the editor's API key injected."""
    settings = EditorSettings.get()
    url = urljoin(str(settings.backend_api_url), f"v0/{path}")
    headers = {
        k: v for k, v in request.headers.items() if k.lower() in _FORWARD_REQUEST
    }
    headers["X-API-Key"] = settings.backend_api_key.get_secret_value()
    body = await request.body()
    upstream = await run_in_threadpool(
        partial(
            requests.request,
            method=request.method,
            url=url,
            params=request.query_params.multi_items(),
            headers=headers,
            data=body,
            timeout=30,
        )
    )
    if upstream.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        logger.warning(
            "backend proxy %s %s -> %s", request.method, url, upstream.status_code
        )
    response_headers = {
        k: v for k, v in upstream.headers.items() if k.lower() not in _STRIP_RESPONSE
    }
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
        media_type=upstream.headers.get("content-type"),
    )
