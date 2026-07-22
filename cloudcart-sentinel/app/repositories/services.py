from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MonitoredService, ProbeResult, ProbeStatus
from app.schemas import ServiceCreate


class ServiceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: ServiceCreate) -> MonitoredService:
        service = MonitoredService(**payload.model_dump())
        self.session.add(service)
        await self.session.commit()
        await self.session.refresh(service)
        return service

    async def list(self) -> list[MonitoredService]:
        result = await self.session.scalars(
            select(MonitoredService).order_by(MonitoredService.name)
        )
        return list(result)

    async def get(self, service_id: UUID) -> MonitoredService | None:
        return await self.session.get(MonitoredService, service_id)

    async def save_probe(self, probe: ProbeResult) -> ProbeResult:
        self.session.add(probe)
        await self.session.commit()
        await self.session.refresh(probe)
        return probe

    async def recent_probes(self, service_id: UUID, limit: int = 100) -> list[ProbeResult]:
        rows = await self.session.scalars(
            select(ProbeResult)
            .where(ProbeResult.service_id == service_id)
            .order_by(desc(ProbeResult.started_at))
            .limit(limit)
        )
        return list(rows)

    async def availability(self, service_id: UUID, limit: int = 100) -> tuple[int, int]:
        subquery = (
            select(ProbeResult.status)
            .where(ProbeResult.service_id == service_id)
            .order_by(desc(ProbeResult.started_at))
            .limit(limit)
            .subquery()
        )
        row = (
            await self.session.execute(
                select(
                    func.count().label("total"),
                    func.count().filter(subquery.c.status == ProbeStatus.HEALTHY).label("healthy"),
                ).select_from(subquery)
            )
        ).one()
        return int(row.total), int(row.healthy)
