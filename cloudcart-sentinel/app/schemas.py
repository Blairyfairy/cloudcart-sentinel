from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

ServiceKind = Literal["http", "postgres", "redis", "dns"]


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ServiceCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=120, pattern=r"^[a-zA-Z0-9_-]+$")]
    kind: ServiceKind
    target: str
    interval_seconds: int = Field(default=60, ge=15, le=86400)
    timeout_seconds: int = Field(default=5, ge=1, le=60)
    slo_target: float = Field(default=99.9, ge=90, le=100)


class ServiceRead(ServiceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    enabled: bool
    created_at: datetime
    updated_at: datetime


class ProbeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    service_id: UUID
    started_at: datetime
    finished_at: datetime
    status: str
    latency_ms: float
    status_code: int | None
    error: str | None


class SLORead(BaseModel):
    service_id: UUID
    sample_size: int
    availability_percent: float
    target_percent: float
    budget_remaining_percent: float
    meeting_slo: bool
