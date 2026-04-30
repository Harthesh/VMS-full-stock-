from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status as http_status
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.core.enums import EmergencyStatus, RoleKey
from app.db.session import get_db
from app.models.rbac import User
from app.schemas.emergency import (
    ContactTraceCreate,
    ContactTraceRead,
    EmergencyEventListItem,
    EmergencyEventRead,
    EmergencyResolve,
    EmergencyTrigger,
    HealthScreeningCreate,
    HealthScreeningRead,
    MusterRead,
    MusterUpdate,
)
from app.services.emergency_service import (
    create_contact_trace,
    create_health_screening,
    event_summary,
    get_event_or_404,
    get_event_with_musters,
    get_muster_or_404,
    list_contact_traces,
    list_events,
    list_health_screenings,
    resolve_event,
    trigger_emergency,
    update_muster,
)

router = APIRouter()


@router.post(
    "/events",
    response_model=EmergencyEventRead,
    status_code=http_status.HTTP_201_CREATED,
)
def trigger(
    payload: EmergencyTrigger,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.ADMIN, RoleKey.GATEKEEPER)),
) -> EmergencyEventRead:
    event = trigger_emergency(db, payload, actor)
    db.commit()
    return get_event_with_musters(db, event.id)


@router.get("/events", response_model=list[EmergencyEventListItem])
def list_emergency_events(
    status_filter: EmergencyStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.ADMIN, RoleKey.GATEKEEPER, RoleKey.HR)),
) -> list[EmergencyEventListItem]:
    return list_events(db, status_filter=status_filter)


@router.get("/events/{event_id}", response_model=EmergencyEventRead)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.ADMIN, RoleKey.GATEKEEPER, RoleKey.HR)),
) -> EmergencyEventRead:
    return get_event_with_musters(db, event_id)


@router.get("/events/{event_id}/summary")
def get_event_summary(
    event_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.ADMIN, RoleKey.GATEKEEPER, RoleKey.HR)),
) -> dict:
    event = get_event_or_404(db, event_id)
    return event_summary(db, event)


@router.post("/events/{event_id}/resolve", response_model=EmergencyEventRead)
def resolve(
    event_id: int,
    payload: EmergencyResolve,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.ADMIN)),
) -> EmergencyEventRead:
    event = get_event_or_404(db, event_id)
    resolve_event(db, event, payload, actor)
    db.commit()
    return get_event_with_musters(db, event.id)


@router.patch("/musters/{muster_id}", response_model=MusterRead)
def patch_muster(
    muster_id: int,
    payload: MusterUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.ADMIN, RoleKey.GATEKEEPER)),
) -> MusterRead:
    muster = get_muster_or_404(db, muster_id)
    update_muster(db, muster, payload, actor)
    db.commit()
    db.refresh(muster)
    return muster


# Health screenings
@router.post(
    "/health-screenings",
    response_model=HealthScreeningRead,
    status_code=http_status.HTTP_201_CREATED,
)
def post_health_screening(
    payload: HealthScreeningCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.GATEKEEPER, RoleKey.ADMIN)),
) -> HealthScreeningRead:
    rec = create_health_screening(db, payload, actor)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/health-screenings", response_model=list[HealthScreeningRead])
def get_health_screenings(
    visitor_request_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.GATEKEEPER, RoleKey.ADMIN, RoleKey.HR)),
) -> list[HealthScreeningRead]:
    return list_health_screenings(db, visitor_request_id=visitor_request_id)


# Contact trace
@router.post(
    "/contact-trace",
    response_model=ContactTraceRead,
    status_code=http_status.HTTP_201_CREATED,
)
def post_contact_trace(
    payload: ContactTraceCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.ADMIN, RoleKey.HR)),
) -> ContactTraceRead:
    rec = create_contact_trace(db, payload, actor)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/contact-trace", response_model=list[ContactTraceRead])
def get_contact_traces(
    source_visitor_request_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.ADMIN, RoleKey.HR)),
) -> list[ContactTraceRead]:
    return list_contact_traces(db, source_visitor_request_id=source_visitor_request_id)
