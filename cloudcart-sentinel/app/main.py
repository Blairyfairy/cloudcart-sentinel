import time
from contextlib import asynccontextmanager
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from redis.asyncio import Redis
from sqlalchemy import text

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.metrics import REQUEST_COUNT, REQUEST_LATENCY
from app.db.session import engine

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("application_started", environment=settings.environment)
    yield
    await engine.dispose()
    logger.info("application_stopped")


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.middleware("http")
async def telemetry(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    structlog.contextvars.bind_contextvars(request_id=request_id)
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed", method=request.method, path=request.url.path)
        raise
    elapsed = time.perf_counter() - started
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)
    REQUEST_COUNT.labels(request.method, path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
    response.headers["x-request-id"] = request_id
    logger.info(
        "request_completed",
        method=request.method,
        path=path,
        status=response.status_code,
        duration_ms=round(elapsed * 1000, 2),
    )
    structlog.contextvars.clear_contextvars()
    return response


@app.get("/health/live", tags=["health"])
async def live() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
async def ready() -> dict[str, str]:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    redis = Redis.from_url(settings.redis_url)
    try:
        await redis.ping()
    finally:
        await redis.aclose()
    return {"status": "ready"}


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
