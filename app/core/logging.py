import logging
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("atoma")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    # Silence noisy third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured request/response logger.
    Attaches a unique X-Request-ID to every request for traceability.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]
        client_host = request.client.host if request.client else "unknown"
        start_time = time.perf_counter()

        logger.info(
            f"[{request_id}] --> {request.method} {request.url.path} "
            f"client={client_host}"
        )

        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"[{request_id}] <-- {request.method} {request.url.path} "
            f"status={response.status_code} duration={duration_ms:.1f}ms"
        )

        # Surface the request ID in response headers for debugging
        response.headers["X-Request-ID"] = request_id
        return response
