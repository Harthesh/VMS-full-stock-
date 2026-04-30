from __future__ import annotations

import secrets
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import (
    ApprovalActionType,
    InvitationStatus,
    VisitorRequestStatus,
    VisitorType,
)
from app.models.invitation import VisitorInvitation
from app.models.rbac import User
from app.models.visitor import VisitorRequest
from app.models.workflow import ApprovalAction
from app.schemas.invitation import (
    InvitationCreate,
    InvitationPublicSubmit,
)
from app.services.audit_service import record_audit_log
from app.services.badge_service import ensure_badge
from app.services.email_service import (
    send_bulk_email,
    send_visitor_approval_email,
    send_vip_alert_email,
)
from app.services.visitor_request_service import generate_request_no
from app.services.workflow_service import build_approval_steps


def _generate_token() -> str:
    return secrets.token_urlsafe(32)


def create_invitation(
    db: Session, payload: InvitationCreate, host: User
) -> VisitorInvitation:
    if payload.visit_date < date.today():
        raise HTTPException(status_code=400, detail="visit_date cannot be in the past")
    days = max(1, min(60, payload.expires_in_days))
    inv = VisitorInvitation(
        token=_generate_token(),
        host_user_id=host.id,
        department_id=payload.department_id or host.department_id,
        visitor_name=payload.visitor_name,
        visitor_email=payload.visitor_email,
        visitor_mobile=payload.visitor_mobile,
        company_name=payload.company_name,
        visitor_type=payload.visitor_type,
        visit_date=payload.visit_date,
        visit_time=payload.visit_time,
        purpose=payload.purpose,
        expires_at=datetime.now(timezone.utc) + timedelta(days=days),
        status=InvitationStatus.PENDING,
    )
    db.add(inv)
    db.flush()
    record_audit_log(
        db,
        entity_type="VisitorInvitation",
        entity_id=inv.id,
        action="invitation.create",
        actor_user_id=host.id,
        details={"visitor_name": inv.visitor_name, "visit_date": inv.visit_date.isoformat()},
    )
    return inv


def send_invitation_email(
    db: Session, invitation: VisitorInvitation, *, public_link: str
) -> None:
    if not invitation.visitor_email:
        return
    host_name = invitation.host.full_name if invitation.host else "your host"
    subject = f"You're invited to visit — {host_name}"
    text = "\n".join(
        [
            f"Hello {invitation.visitor_name},",
            "",
            f"{host_name} has invited you for a visit on {invitation.visit_date.isoformat()}"
            + (f" at {invitation.visit_time.strftime('%H:%M')}" if invitation.visit_time else "")
            + ".",
            f"Purpose: {invitation.purpose}",
            "",
            "Please complete your pre-registration using this link:",
            public_link,
            "",
            f"This link expires on {invitation.expires_at.strftime('%Y-%m-%d %H:%M %Z')}.",
        ]
    )
    html = (
        f"<p>Hello {invitation.visitor_name},</p>"
        f"<p><strong>{host_name}</strong> has invited you for a visit on "
        f"<strong>{invitation.visit_date.isoformat()}</strong>"
        + (
            f" at <strong>{invitation.visit_time.strftime('%H:%M')}</strong>"
            if invitation.visit_time
            else ""
        )
        + ".</p>"
        f"<p><strong>Purpose:</strong> {invitation.purpose}</p>"
        f"<p>Please complete your pre-registration using this link:</p>"
        f"<p><a href='{public_link}'>{public_link}</a></p>"
        f"<p style='color:#78716c'>This link expires on {invitation.expires_at.strftime('%Y-%m-%d %H:%M %Z')}.</p>"
    )
    send_bulk_email(
        db,
        event_type="invitation_email",
        recipients=[invitation.visitor_email],
        subject=subject,
        text_body=text,
        html_body=html,
        payload={"invitation_id": invitation.id, "token": invitation.token},
    )


def list_invitations(
    db: Session, actor: User, *, only_mine: bool
) -> list[VisitorInvitation]:
    stmt = (
        select(VisitorInvitation)
        .options(selectinload(VisitorInvitation.host))
        .order_by(VisitorInvitation.created_at.desc())
    )
    if only_mine:
        stmt = stmt.where(VisitorInvitation.host_user_id == actor.id)
    return list(db.execute(stmt).scalars().all())


def get_invitation_or_404(db: Session, invitation_id: int) -> VisitorInvitation:
    obj = db.get(VisitorInvitation, invitation_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    return obj


def cancel_invitation(
    db: Session, invitation: VisitorInvitation, actor: User
) -> VisitorInvitation:
    if invitation.host_user_id != actor.id and not any(
        r.key == "admin" for r in actor.roles
    ):
        raise HTTPException(status_code=403, detail="You cannot cancel this invitation")
    if invitation.status not in (InvitationStatus.PENDING,):
        raise HTTPException(
            status_code=400, detail=f"Cannot cancel an invitation in status {invitation.status.value}"
        )
    invitation.status = InvitationStatus.CANCELLED
    db.flush()
    record_audit_log(
        db,
        entity_type="VisitorInvitation",
        entity_id=invitation.id,
        action="invitation.cancel",
        actor_user_id=actor.id,
        details={},
    )
    return invitation


def get_by_token(db: Session, token: str) -> VisitorInvitation:
    inv = db.execute(
        select(VisitorInvitation)
        .options(selectinload(VisitorInvitation.host))
        .where(VisitorInvitation.token == token)
    ).scalar_one_or_none()
    if inv is None:
        raise HTTPException(status_code=404, detail="Invitation not found")
    # Auto-expire if past expiry and still pending
    if inv.status == InvitationStatus.PENDING and inv.expires_at < datetime.now(timezone.utc):
        inv.status = InvitationStatus.EXPIRED
        db.flush()
    return inv


def submit_invitation(
    db: Session, invitation: VisitorInvitation, payload: InvitationPublicSubmit
) -> VisitorRequest:
    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"This invitation is {invitation.status.value} and cannot be used",
        )
    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = InvitationStatus.EXPIRED
        db.flush()
        raise HTTPException(status_code=400, detail="This invitation has expired")

    # Build the VisitorRequest from the merged invitation + visitor-supplied data.
    visitor_request = VisitorRequest(
        request_no=generate_request_no(db),
        request_date=date.today(),
        requested_by_user_id=invitation.host_user_id,
        host_user_id=invitation.host_user_id,
        department_id=invitation.department_id,
        visitor_type=invitation.visitor_type,
        visit_date=invitation.visit_date,
        visit_time=invitation.visit_time,
        visitor_name=payload.visitor_name or invitation.visitor_name,
        company_name=payload.company_name or invitation.company_name,
        mobile=payload.mobile,
        email=payload.visitor_email or invitation.visitor_email,
        id_proof_type=payload.id_proof_type,
        id_proof_number=payload.id_proof_number,
        purpose=payload.purpose or invitation.purpose,
        remarks=payload.remarks,
        status=VisitorRequestStatus.DRAFT,
        current_approval_level=0,
    )
    db.add(visitor_request)
    db.flush()

    # Auto-submit so it enters the approval flow.
    previous_status = visitor_request.status.value
    if visitor_request.visitor_type == VisitorType.CANDIDATE:
        visitor_request.status = VisitorRequestStatus.SCHEDULED
    else:
        steps = build_approval_steps(visitor_request)
        for step in steps:
            visitor_request.approval_steps.append(step)
        if not steps:
            visitor_request.status = VisitorRequestStatus.APPROVED
            ensure_badge(db, visitor_request)
            send_visitor_approval_email(db, visitor_request)
        else:
            visitor_request.status = VisitorRequestStatus(
                visitor_request.approval_steps[0].pending_status
            )
            visitor_request.current_approval_level = 1

    db.add(
        ApprovalAction(
            visitor_request=visitor_request,
            action=ApprovalActionType.SUBMIT,
            action_by_user_id=invitation.host_user_id,
            from_status=previous_status,
            to_status=visitor_request.status.value,
            remarks="Submitted via pre-registration invitation",
        )
    )
    db.flush()

    if visitor_request.visitor_type == VisitorType.VIP_CUSTOMER:
        send_vip_alert_email(db, visitor_request)

    invitation.status = InvitationStatus.USED
    invitation.used_at = datetime.now(timezone.utc)
    invitation.visitor_request_id = visitor_request.id
    db.flush()

    record_audit_log(
        db,
        entity_type="VisitorInvitation",
        entity_id=invitation.id,
        action="invitation.submit",
        actor_user_id=invitation.host_user_id,
        details={"visitor_request_id": visitor_request.id},
    )
    return visitor_request
