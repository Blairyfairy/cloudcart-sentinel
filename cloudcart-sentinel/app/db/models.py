from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class ServiceKind(StrEnum):
    HTTP = "http"
    POSTGRES = "postgres"
    REDIS = "redis"
    DNS = "dns"


class ProbeStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class MonitoredService(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "monitored_services"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(24))
    target: Mapped[str] = mapped_column(String(2048))
    interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=5)
    slo_target: Mapped[float] = mapped_column(Float, default=99.9)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    probes: Mapped[list["ProbeResult"]] = relationship(
        back_populates="service", cascade="all, delete-orphan"
    )


class ProbeResult(UUIDMixin, Base):
    __tablename__ = "probe_results"

    service_id: Mapped[UUID] = mapped_column(
        ForeignKey("monitored_services.id", ondelete="CASCADE"), index=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(24), index=True)
    latency_ms: Mapped[float] = mapped_column(Float)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    service: Mapped[MonitoredService] = relationship(back_populates="probes")
