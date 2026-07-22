from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, SessionDep, SettingsDep
from app.core.security import create_access_token
from app.repositories.services import ServiceRepository
from app.schemas import ProbeRead, ServiceCreate, ServiceRead, SLORead, TokenRequest, TokenResponse
from app.services.probes import ProbeRunner
from app.services.slo import calculate_slo

router = APIRouter(prefix="/api/v1")


@router.post("/auth/token", response_model=TokenResponse, tags=["auth"])
async def token(payload: TokenRequest, settings: SettingsDep) -> TokenResponse:
    # Local showcase auth. Production deployment should use an external IdP or stored password hash.
    if payload.username != settings.admin_username or payload.password != settings.admin_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    return TokenResponse(access_token=create_access_token(payload.username, settings))


@router.post("/services", response_model=ServiceRead, status_code=201, tags=["services"])
async def create_service(
    payload: ServiceCreate, session: SessionDep, _: CurrentUser
) -> ServiceRead:
    service = await ServiceRepository(session).create(payload)
    return ServiceRead.model_validate(service)


@router.get("/services", response_model=list[ServiceRead], tags=["services"])
async def list_services(session: SessionDep, _: CurrentUser) -> list[ServiceRead]:
    services = await ServiceRepository(session).list()
    return [ServiceRead.model_validate(service) for service in services]


@router.post("/services/{service_id}/probe", response_model=ProbeRead, tags=["probes"])
async def run_probe(service_id: UUID, session: SessionDep, _: CurrentUser) -> ProbeRead:
    repository = ServiceRepository(session)
    service = await repository.get(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="service not found")
    probe = await ProbeRunner().run(service)
    return ProbeRead.model_validate(await repository.save_probe(probe))


@router.get("/services/{service_id}/probes", response_model=list[ProbeRead], tags=["probes"])
async def recent_probes(
    service_id: UUID,
    session: SessionDep,
    _: CurrentUser,
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[ProbeRead]:
    rows = await ServiceRepository(session).recent_probes(service_id, limit)
    return [ProbeRead.model_validate(row) for row in rows]


@router.get("/services/{service_id}/slo", response_model=SLORead, tags=["slo"])
async def get_slo(service_id: UUID, session: SessionDep, _: CurrentUser) -> SLORead:
    repository = ServiceRepository(session)
    service = await repository.get(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="service not found")
    total, healthy = await repository.availability(service_id)
    return calculate_slo(service.id, total, healthy, service.slo_target)
