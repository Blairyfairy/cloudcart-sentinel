from uuid import uuid4
import pytest
from app.db.models import MonitoredService, ProbeStatus, ServiceKind
from app.services.probes import ProbeOutcome, ProbeRunner

@pytest.mark.asyncio
async def test_runner_persists_boundary_failure(monkeypatch):
    service = MonitoredService(id=uuid4(), name="bad", kind=ServiceKind.HTTP, target="https://invalid", interval_seconds=60, timeout_seconds=1, slo_target=99.9)
    async def explode(_): raise RuntimeError("boom")
    monkeypatch.setattr(ProbeRunner, "_dispatch", explode)
    result = await ProbeRunner().run(service)
    assert result.status == ProbeStatus.DOWN
    assert "RuntimeError" in (result.error or "")
