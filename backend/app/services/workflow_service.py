from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import has_any_role
from app.core.enums import (
    ApprovalActionType,
    ApprovalStepStatus,
    RoleKey,
    VisitorRequestStatus,
    VisitorType,
)
from app.models.rbac import User
from app.models.visitor import VisitorRequest
from app.models.workflow import ApprovalAction, ApprovalStep
from app.services.audit_service import record_audit_log
from app.services.badge_service import ensure_badge
from app.services.email_service import send_visitor_approval_email
from app.services.notification_service import queue_notifications
from app.workflows.definitions import CREATOR_ROLE_RULES, build_workflow


def validate_creator_permissions(visitor_type: VisitorType, actor: User) -> None:
    allowed_roles = CREATOR_ROLE_RULES.get(visitor_type, set())
    if has_any_role(actor, {RoleKey.ADMIN}) or has_any_role(actor, allowed_roles):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"{visitor_type.value.replace('_', ' ').title()} requests cannot be created by your role",
    )


def build_approval_steps(visitor_request: VisitorRequest) -> list[ApprovalStep]:
    definitions = build_workflow(
        visitor_request.visitor_type,
        requires_it_access=visitor_request.requires_it_access,
        requires_hospitality=visitor_request.requires_hospitality,
    )
    steps: list[ApprovalStep] = []
    for index, definition in enumerate(definitions, start=1):
        steps.append(
            ApprovalStep(
                step_order=index,
                step_key=definition.step_key,
                step_name=definition.step_name,
                role_key=definition.role_key.value,
                pending_status=definition.pending_status.value,
                status=ApprovalStepStatus.ACTIVE if index == 1 else ApprovalStepStatus.QUEUED,
            )
        )
    return steps


def submit_request(db: Session, visitor_request: VisitorRequest, actor: User) -> VisitorRequest:
    if visitor_request.status not in {VisitorRequestStatus.DRAFT, VisitorRequestStatus.SENT_BACK}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft requests can be submitted")

    visitor_request.approval_steps.clear()
    db.flush()

    previous_status = visitor_request.status.value
    if visitor_request.visitor_type == VisitorType.CANDIDATE:
        visitor_request.status = VisitorRequestStatus.SCHEDULED
        visitor_request.current_approval_level = 0
    else:
        steps = build_approval_steps(visitor_request)
        for step in steps:
            visitor_request.approval_steps.append(step)
        if not steps:
            visitor_request.status = VisitorRequestStatus.APPROVED
            ensure_badge(db, visitor_request)
            send_visitor_approval_email(db, visitor_request)
        else:
            visitor_request.status = VisitorRequestStatus(visitor_request.approval_steps[0].pending_status)
            visitor_request.current_approval_level = 1

    action = ApprovalAction(
        visitor_request=visitor_request,
        action=ApprovalActionType.SUBMIT,
        action_by_user_id=actor.id,
        from_status=previous_status,
        to_status=visitor_request.status.value,
    )
    db.add(action)
    record_audit_log(
        db,
        entity_type="visitor_request",
        entity_id=visitor_request.id,
        action="submitted",
        actor_user_id=actor.id,
        details={"status": visitor_request.status.value},
    )
    recipient_ids = [visitor_request.host_user_id] if visitor_request.host_user_id else []
    if recipient_ids:
        queue_notifications(
            db,
            recipient_user_ids=recipient_ids,
            event_type="request_submitted",
            title=f"Request {visitor_request.request_no} submitted",
            message=f"{visitor_request.visitor_name} has been submitted for visit on {visitor_request.visit_date.isoformat()}",
            payload={"request_id": visitor_request.id},
        )
    db.flush()
    return visitor_request


def get_pending_approvals_for_user(db: Session, actor: User) -> list[VisitorRequest]:
    role_keys = [role.key for role in actor.roles]
    statement = (
        select(VisitorRequest)
        .join(ApprovalStep, ApprovalStep.visitor_request_id == VisitorRequest.id)
        .where(ApprovalStep.status == ApprovalStepStatus.ACTIVE)
        .where(ApprovalStep.role_key.in_(role_keys))
        .options(
            selectinload(VisitorRequest.requested_by),
            selectinload(VisitorRequest.host_user),
            selectinload(VisitorRequest.approval_steps),
        )
        .order_by(VisitorRequest.visit_date.asc())
    )
    return list(db.execute(statement).scalars().unique().all())


def apply_approval_action(
    db: Session, visitor_request: VisitorRequest, *, action_type: ApprovalActionType, remarks: str | None, actor: User
) -> VisitorRequest:
    active_step = next((step for step in visitor_request.approval_steps if step.status == ApprovalStepStatus.ACTIVE), None)
    if not active_step:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active approval step found")

    if not (has_any_role(actor, {RoleKey.ADMIN}) or has_any_role(actor, {active_step.role_key})):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot act on this approval")

    previous_status = visitor_request.status.value

    if action_type == ApprovalActionType.APPROVE:
        active_step.status = ApprovalStepStatus.APPROVED
        active_step.assigned_user_id = actor.id
        active_step.remarks = remarks
        next_step = next(
            (step for step in sorted(visitor_request.approval_steps, key=lambda item: item.step_order) if step.status == ApprovalStepStatus.QUEUED),
            None,
        )
        if next_step:
            next_step.status = ApprovalStepStatus.ACTIVE
            visitor_request.current_approval_level = next_step.step_order
            visitor_request.status = VisitorRequestStatus(next_step.pending_status)
        else:
            visitor_request.current_approval_level = active_step.step_order
            visitor_request.status = VisitorRequestStatus.APPROVED
            ensure_badge(db, visitor_request)
            send_visitor_approval_email(db, visitor_request)
    elif action_type == ApprovalActionType.REJECT:
        active_step.status = ApprovalStepStatus.REJECTED
        active_step.assigned_user_id = actor.id
        active_step.remarks = remarks
        visitor_request.status = VisitorRequestStatus.REJECTED
    elif action_type == ApprovalActionType.SEND_BACK:
        active_step.status = ApprovalStepStatus.SENT_BACK
        active_step.assigned_user_id = actor.id
        active_step.remarks = remarks
        for step in visitor_request.approval_steps:
            if step.id != active_step.id and step.status == ApprovalStepStatus.QUEUED:
                step.status = ApprovalStepStatus.CANCELLED
        visitor_request.current_approval_level = 0
        visitor_request.status = VisitorRequestStatus.SENT_BACK
    elif action_type == ApprovalActionType.CANCEL:
        active_step.status = ApprovalStepStatus.CANCELLED
        active_step.assigned_user_id = actor.id
        active_step.remarks = remarks
        for step in visitor_request.approval_steps:
            if step.id != active_step.id and step.status in {ApprovalStepStatus.QUEUED, ApprovalStepStatus.ACTIVE}:
                step.status = ApprovalStepStatus.CANCELLED
        visitor_request.status = VisitorRequestStatus.CANCELLED
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported approval action")

    db.add(
        ApprovalAction(
            visitor_request_id=visitor_request.id,
            approval_step_id=active_step.id,
            action=action_type,
            action_by_user_id=actor.id,
            remarks=remarks,
            from_status=previous_status,
            to_status=visitor_request.status.value,
        )
    )
    record_audit_log(
        db,
        entity_type="visitor_request",
        entity_id=visitor_request.id,
        action=action_type.value,
        actor_user_id=actor.id,
        details={"from_status": previous_status, "to_status": visitor_request.status.value},
    )
    recipient_ids = [visitor_request.requested_by_user_id]
    if visitor_request.host_user_id and visitor_request.host_user_id != visitor_request.requested_by_user_id:
        recipient_ids.append(visitor_request.host_user_id)
    queue_notifications(
        db,
        recipient_user_ids=recipient_ids,
        event_type=f"request_{action_type.value}",
        title=f"Request {visitor_request.request_no} {action_type.value.replace('_', ' ')}",
        message=f"{visitor_request.visitor_name} is now {visitor_request.status.value.replace('_', ' ')}",
        payload={"request_id": visitor_request.id},
    )
    db.flush()
    return visitor_request


def load_request_with_workflow(db: Session, request_id: int) -> VisitorRequest | None:
    statement = (
        select(VisitorRequest)
        .where(VisitorRequest.id == request_id)
        .options(
            selectinload(VisitorRequest.requested_by).selectinload(User.roles),
            selectinload(VisitorRequest.host_user),
            selectinload(VisitorRequest.department),
            selectinload(VisitorRequest.approval_steps),
            selectinload(VisitorRequest.approval_actions).selectinload(ApprovalAction.action_by),
            selectinload(VisitorRequest.badge),
            selectinload(VisitorRequest.hospitality_request),
            selectinload(VisitorRequest.documents),
        )
    )
    return db.execute(statement).scalar_one_or_none()
