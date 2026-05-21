import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("aerohub.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        logger.info(
            "[%s] → %s %s  client=%s",
            request_id, request.method, request.url.path,
            request.client.host if request.client else "unknown",
        )

        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "[%s] ← %s %s  status=%d  %.1fms",
            request_id, request.method, request.url.path,
            response.status_code, elapsed_ms,
        )
        response.headers["X-Request-ID"] = request_id
        return response
