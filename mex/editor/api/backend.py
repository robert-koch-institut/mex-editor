from functools import partial

from fastapi import APIRouter, Request, Response
from starlette import status
from starlette.concurrency import run_in_threadpool

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger

router = APIRouter()

_FORWARD_REQUEST = frozenset({"content-type", "accept", "x-forwarded-for"})
_STRIP_RESPONSE = frozenset({"content-length", "transfer-encoding", "connection"})


@router.api_route(
    "/backend/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE"],
)
async def backend_proxy(path: str, request: Request) -> Response:
    """Forward a request to the mex-backend with the editor's API key injected.

    Uses the session of the `BackendApiConnector`, which carries the backend URL,
    the API key and the `verify_session` setting. We call the session directly
    instead of `request_raw`, because that would raise on non-2xx responses and
    retry on 5xx/429, which a transparent proxy must not do (e.g. for POSTs).
    """
    connector = await run_in_threadpool(BackendApiConnector.get)
    url = f"{connector.url.rstrip('/')}/{path}"
    headers = {
        k: v for k, v in request.headers.items() if k.lower() in _FORWARD_REQUEST
    }
    body = await request.body()
    upstream = await run_in_threadpool(
        partial(
            connector.session.request,
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
