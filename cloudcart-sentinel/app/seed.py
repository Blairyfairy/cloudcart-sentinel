import asyncio

from sqlalchemy import select

from app.db.models import MonitoredService, ServiceKind
from app.db.session import SessionFactory


async def seed() -> None:
    async with SessionFactory() as session:
        exists = await session.scalar(select(MonitoredService.id).limit(1))
        if exists:
            return
        session.add_all(
            [
                MonitoredService(
                    name="demo-storefront",
                    kind=ServiceKind.HTTP,
                    target="https://example.com",
                    interval_seconds=60,
                    timeout_seconds=5,
                    slo_target=99.9,
                ),
                MonitoredService(
                    name="primary-dns",
                    kind=ServiceKind.DNS,
                    target="example.com",
                    interval_seconds=300,
                    timeout_seconds=5,
                    slo_target=99.99,
                ),
            ]
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
