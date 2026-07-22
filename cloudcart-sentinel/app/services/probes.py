import asyncio
import time
from dataclasses import dataclass
from datetime import UTC, datetime

import dns.asyncresolver
import httpx
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.metrics import PROBE_COUNT, PROBE_LATENCY
from app.db.models import MonitoredService, ProbeResult, ProbeStatus, ServiceKind


@dataclass(slots=True)
class ProbeOutcome:
    status: ProbeStatus
    latency_ms: float
    status_code: int | None = None
    error: str | None = None


class ProbeRunner:
    async def run(self, service: MonitoredService) -> ProbeResult:
        started = datetime.now(UTC)
        clock = time.perf_counter()
        try:
            outcome = await asyncio.wait_for(
                self._dispatch(service), timeout=service.timeout_seconds
            )
        except TimeoutError:
            outcome = ProbeOutcome(ProbeStatus.DOWN, 0, error="probe timeout")
        except Exception as exc:  # boundary: persist failure instead of crashing worker
            outcome = ProbeOutcome(ProbeStatus.DOWN, 0, error=f"{type(exc).__name__}: {exc}")
        elapsed_ms = (time.perf_counter() - clock) * 1000
        if outcome.latency_ms == 0:
            outcome.latency_ms = elapsed_ms
        finished = datetime.now(UTC)
        PROBE_COUNT.labels(service.kind, outcome.status.value).inc()
        PROBE_LATENCY.labels(service.kind).observe(outcome.latency_ms / 1000)
        return ProbeResult(
            service_id=service.id,
            started_at=started,
            finished_at=finished,
            status=outcome.status.value,
            latency_ms=round(outcome.latency_ms, 2),
            status_code=outcome.status_code,
            error=outcome.error,
        )

    async def _dispatch(self, service: MonitoredService) -> ProbeOutcome:
        match service.kind:
            case ServiceKind.HTTP:
                return await self._http(service.target)
            case ServiceKind.POSTGRES:
                return await self._postgres(service.target)
            case ServiceKind.REDIS:
                return await self._redis(service.target)
            case ServiceKind.DNS:
                return await self._dns(service.target)
            case _:
                raise ValueError(f"unsupported service kind: {service.kind}")

    async def _http(self, target: str) -> ProbeOutcome:
        start = time.perf_counter()
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(target)
        latency = (time.perf_counter() - start) * 1000
        status = ProbeStatus.HEALTHY if response.status_code < 400 else ProbeStatus.DEGRADED
        return ProbeOutcome(status, latency, response.status_code)

    async def _postgres(self, target: str) -> ProbeOutcome:
        start = time.perf_counter()
        engine = create_async_engine(target, pool_pre_ping=True)
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        finally:
            await engine.dispose()
        return ProbeOutcome(ProbeStatus.HEALTHY, (time.perf_counter() - start) * 1000)

    async def _redis(self, target: str) -> ProbeOutcome:
        start = time.perf_counter()
        client = Redis.from_url(target, socket_connect_timeout=3)
        try:
            healthy = await client.ping()
        finally:
            await client.aclose()
        status = ProbeStatus.HEALTHY if healthy else ProbeStatus.DOWN
        return ProbeOutcome(status, (time.perf_counter() - start) * 1000)

    async def _dns(self, target: str) -> ProbeOutcome:
        start = time.perf_counter()
        answers = await dns.asyncresolver.resolve(target, "A")
        status = ProbeStatus.HEALTHY if list(answers) else ProbeStatus.DOWN
        return ProbeOutcome(status, (time.perf_counter() - start) * 1000)
