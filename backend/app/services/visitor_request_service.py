from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import has_any_role
from app.core.enums import ApprovalActionType, RoleKey, VisitorRequestStatus
from app.models.rbac import User
from app.models.visitor import HospitalityRequest, InterviewPanelMember, VisitorRequest
from app.models.workflow import ApprovalAction
from app.schemas.visitor_request import VisitorRequestCreate, VisitorRequestUpdate
from app.services.audit_service import record_audit_log
from app.services.workflow_service import load_request_with_workflow, submit_request, validate_creator_permissions


PRIVILEGED_VIEW_ROLES = {
    RoleKey.ADMIN,
    RoleKey.HR,
    RoleKey.BD_SALES,
    RoleKey.MANAGER,
    RoleKey.HOD,
    RoleKey.CEO_OFFICE,
    RoleKey.SECURITY,
    RoleKey.IT,
    RoleKey.GATEKEEPER,
}


def generate_request_no(db: Session) -> str:
    latest_id = db.execute(select(VisitorRequest.id).order_by(VisitorRequest.id.desc())).scalar() or 0
    return f"VR-{date.today().strftime('%Y%m%d')}-{latest_id + 1:05d}-{uuid4().hex[:4].upper()}"


def list_requests(db: Session, actor: User) -> list[VisitorRequest]:
    statement = (
        select(VisitorRequest)
        .options(
            selectinload(VisitorRequest.requested_by),
            selectinload(VisitorRequest.host_user),
            selectinload(VisitorRequest.department),
            selectinload(VisitorRequest.badge),
            selectinload(VisitorRequest.hospitality_request),
        )
        .order_by(VisitorRequest.created_at.desc())
    )
    if not has_any_role(actor, PRIVILEGED_VIEW_ROLES):
        statement = statement.where(VisitorRequest.requested_by_user_id == actor.id)
    return list(db.execute(statement).scalars().unique().all())


def get_request_or_404(db: Session, request_id: int) -> VisitorRequest:
    visitor_request = load_request_with_workflow(db, request_id)
    if not visitor_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visitor request not found")
    return visitor_request


def ensure_request_access(visitor_request: VisitorRequest, actor: User) -> None:
    if has_any_role(actor, PRIVILEGED_VIEW_ROLES):
        return
    if visitor_request.requested_by_user_id == actor.id or visitor_request.host_user_id == actor.id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot access this request")


def upsert_hospitality(visitor_request: VisitorRequest, payload: VisitorRequestCreate | VisitorRequestUpdate) -> None:
    if payload.hospitality is None:
        if not visitor_request.requires_hospitality:
            visitor_request.hospitality_request = None
        return

    hospitality_payload = payload.hospitality.model_dump()
    if visitor_request.hospitality_request:
        for key, value in hospitality_payload.items():
            setattr(visitor_request.hospitality_request, key, value)
    else:
        visitor_request.hospitality_request = HospitalityRequest(**hospitality_payload)


def replace_interview_panels(visitor_request: VisitorRequest, user_ids: list[int] | None) -> None:
    if user_ids is None:
        return
    visitor_request.interview_panels.clear()
    for user_id in user_ids:
        visitor_request.interview_panels.append(InterviewPanelMember(panel_member_user_id=user_id))


def create_request(db: Session, payload: VisitorRequestCreate, actor: User) -> VisitorRequest:
    validate_creator_permissions(payload.visitor_type, actor)
    visitor_request = VisitorRequest(
        request_no=generate_request_no(db),
        request_date=date.today(),
        requested_by_user_id=actor.id,
        **payload.model_dump(exclude={"hospitality", "panel_member_user_ids"}),
    )
    db.add(visitor_request)
    db.flush()
    upsert_hospitality(visitor_request, payload)
    replace_interview_panels(visitor_request, payload.panel_member_user_ids)
    record_audit_log(
        db,
        entity_type="visitor_request",
        entity_id=visitor_request.id,
        action="created",
        actor_user_id=actor.id,
        details={"request_no": visitor_request.request_no},
    )
    db.flush()
    db.refresh(visitor_request)
    return get_request_or_404(db, visitor_request.id)


def update_request(db: Session, visitor_request: VisitorRequest, payload: VisitorRequestUpdate, actor: User) -> VisitorRequest:
    ensure_request_access(visitor_request, actor)
    if visitor_request.status not in {VisitorRequestStatus.DRAFT, VisitorRequestStatus.SENT_BACK} and not has_any_role(
        actor, {RoleKey.ADMIN}
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft requests can be edited")

    for key, value in payload.model_dump(exclude_unset=True, exclude={"hospitality", "panel_member_user_ids"}).items():
        setattr(visitor_request, key, value)
    upsert_hospitality(visitor_request, payload)
    replace_interview_panels(visitor_request, payload.panel_member_user_ids)
    record_audit_log(
        db,
        entity_type="visitor_request",
        entity_id=visitor_request.id,
        action="updated",
        actor_user_id=actor.id,
        details=payload.model_dump(exclude_unset=True),
    )
    db.flush()
    return get_request_or_404(db, visitor_request.id)


def submit_existing_request(db: Session, visitor_request: VisitorRequest, actor: User) -> VisitorRequest:
    ensure_request_access(visitor_request, actor)
    updated_request = submit_request(db, visitor_request, actor)
    db.flush()
    return get_request_or_404(db, updated_request.id)


def cancel_request(db: Session, visitor_request: VisitorRequest, actor: User, remarks: str | None) -> VisitorRequest:
    ensure_request_access(visitor_request, actor)
    if visitor_request.status in {VisitorRequestStatus.CHECKED_IN, VisitorRequestStatus.CHECKED_OUT}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Checked-in requests cannot be cancelled")

    previous_status = visitor_request.status.value
    visitor_request.status = VisitorRequestStatus.CANCELLED
    db.add(
        ApprovalAction(
            visitor_request_id=visitor_request.id,
            action=ApprovalActionType.CANCEL,
            action_by_user_id=actor.id,
            remarks=remarks,
            from_status=previous_status,
            to_status=VisitorRequestStatus.CANCELLED.value,
        )
    )
    record_audit_log(
        db,
        entity_type="visitor_request",
        entity_id=visitor_request.id,
        action="cancelled",
        actor_user_id=actor.id,
        details={"remarks": remarks},
    )
    db.flush()
    return get_request_or_404(db, visitor_request.id)
