from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import ApprovalActionType, BadgeStatus, GateAction, VisitorRequestStatus
from app.models.rbac import User
from app.models.visitor import VisitorLog, VisitorRequest
from app.models.workflow import ApprovalAction
from app.services.audit_service import record_audit_log
from app.services.badge_service import ensure_badge
from app.services.blacklist_service import find_blacklist_match
from app.services.notification_service import queue_notifications


ALLOWED_GATE_STATUSES = {
    VisitorRequestStatus.APPROVED,
    VisitorRequestStatus.SCHEDULED,
}


def lookup_request(
    db: Session,
    *,
    qr_code_value: str | None = None,
    request_no: str | None = None,
    visitor_name: str | None = None,
    mobile: str | None = None,
) -> tuple[VisitorRequest, str | None, str | None]:
    statement = (
        select(VisitorRequest)
        .options(
            selectinload(VisitorRequest.requested_by),
            selectinload(VisitorRequest.host_user),
            selectinload(VisitorRequest.department),
            selectinload(VisitorRequest.badge),
            selectinload(VisitorRequest.hospitality_request),
            selectinload(VisitorRequest.approval_steps),
        )
        .order_by(VisitorRequest.visit_date.desc())
    )
    filters = []
    if qr_code_value:
        filters.append(VisitorRequest.qr_code_value == qr_code_value)
    if request_no:
        filters.append(VisitorRequest.request_no == request_no)
    if mobile:
        filters.append(VisitorRequest.mobile == mobile)
    if visitor_name:
        filters.append(VisitorRequest.visitor_name.ilike(f"%{visitor_name}%"))
    if not filters:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide at least one search criteria")
    visitor_request = db.execute(statement.where(or_(*filters))).scalars().first()
    if not visitor_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visitor request not found")

    blacklist = find_blacklist_match(
        db,
        visitor_name=visitor_request.visitor_name,
        mobile=visitor_request.mobile,
        id_proof_number=visitor_request.id_proof_number,
    )
    if blacklist:
        return visitor_request, blacklist.action_type.value, blacklist.reason
    return visitor_request, None, None


def _check_gate_eligibility(visitor_request: VisitorRequest, blacklist_action: str | None) -> None:
    if blacklist_action == "block":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Visitor is blacklisted and access is blocked")
    if visitor_request.status not in ALLOWED_GATE_STATUSES and visitor_request.status != VisitorRequestStatus.CHECKED_IN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Visitor is not approved for gate processing")


def check_in(db: Session, visitor_request: VisitorRequest, actor: User, *, gate_entry_point: str | None, remarks: str | None) -> VisitorRequest:
    blacklist_action, blacklist_reason = None, None
    blacklist = find_blacklist_match(
        db,
        visitor_name=visitor_request.visitor_name,
        mobile=visitor_request.mobile,
        id_proof_number=visitor_request.id_proof_number,
    )
    if blacklist:
        blacklist_action, blacklist_reason = blacklist.action_type.value, blacklist.reason
    if blacklist_action == "block":
        db.add(
            VisitorLog(
                visitor_request_id=visitor_request.id,
                action=GateAction.ACCESS_BLOCKED,
                gate_entry_point=gate_entry_point,
                remarks=blacklist_reason or remarks,
                performed_by_user_id=actor.id,
            )
        )
    _check_gate_eligibility(visitor_request, blacklist_action)
    if visitor_request.status == VisitorRequestStatus.CHECKED_IN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Visitor is already checked in")

    badge = ensure_badge(db, visitor_request)
    visitor_request.status = VisitorRequestStatus.CHECKED_IN
    visitor_request.check_in_time = datetime.now(timezone.utc)
    badge.status = BadgeStatus.ISSUED
    badge.issued_at = visitor_request.check_in_time
    db.add(
        ApprovalAction(
            visitor_request_id=visitor_request.id,
            action=ApprovalActionType.CHECK_IN,
            action_by_user_id=actor.id,
            remarks=remarks or blacklist_reason,
            from_status=visitor_request.status.value,
            to_status=VisitorRequestStatus.CHECKED_IN.value,
        )
    )
    db.add(
        VisitorLog(
            visitor_request_id=visitor_request.id,
            action=GateAction.CHECK_IN if not blacklist_action else GateAction.ACCESS_WARNING,
            gate_entry_point=gate_entry_point,
            remarks=remarks or blacklist_reason,
            performed_by_user_id=actor.id,
        )
    )
    record_audit_log(
        db,
        entity_type="visitor_request",
        entity_id=visitor_request.id,
        action="checked_in",
        actor_user_id=actor.id,
        details={"gate_entry_point": gate_entry_point, "blacklist_action": blacklist_action},
    )
    queue_notifications(
        db,
        recipient_user_ids=[visitor_request.requested_by_user_id],
        event_type="request_checked_in",
        title=f"{visitor_request.visitor_name} checked in",
        message=f"Visitor checked in at {gate_entry_point or 'main gate'}",
        payload={"request_id": visitor_request.id},
    )
    db.flush()
    return visitor_request


def check_out(db: Session, visitor_request: VisitorRequest, actor: User, *, gate_entry_point: str | None, remarks: str | None) -> VisitorRequest:
    if visitor_request.status != VisitorRequestStatus.CHECKED_IN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Visitor is not checked in")
    visitor_request.status = VisitorRequestStatus.CHECKED_OUT
    visitor_request.check_out_time = datetime.now(timezone.utc)
    if visitor_request.badge:
        visitor_request.badge.status = BadgeStatus.RETURNED
        visitor_request.badge.returned_at = visitor_request.check_out_time

    db.add(
        ApprovalAction(
            visitor_request_id=visitor_request.id,
            action=ApprovalActionType.CHECK_OUT,
            action_by_user_id=actor.id,
            remarks=remarks,
            from_status=VisitorRequestStatus.CHECKED_IN.value,
            to_status=VisitorRequestStatus.CHECKED_OUT.value,
        )
    )
    db.add(
        VisitorLog(
            visitor_request_id=visitor_request.id,
            action=GateAction.CHECK_OUT,
            gate_entry_point=gate_entry_point,
            remarks=remarks,
            performed_by_user_id=actor.id,
        )
    )
    record_audit_log(
        db,
        entity_type="visitor_request",
        entity_id=visitor_request.id,
        action="checked_out",
        actor_user_id=actor.id,
        details={"gate_entry_point": gate_entry_point},
    )
    queue_notifications(
        db,
        recipient_user_ids=[visitor_request.requested_by_user_id],
        event_type="request_checked_out",
        title=f"{visitor_request.visitor_name} checked out",
        message=f"Visitor checked out at {gate_entry_point or 'main gate'}",
        payload={"request_id": visitor_request.id},
    )
    db.flush()
    return visitor_request
