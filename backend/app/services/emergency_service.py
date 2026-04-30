from __future__ import annotations

import secrets
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import (
    EmergencyStatus,
    MusterStatus,
    NotificationChannel,
    NotificationStatus,
    RoleKey,
    VisitorRequestStatus,
)
from app.models.emergency import (
    ContactTraceRecord,
    EmergencyEvent,
    EvacuationMuster,
    HealthScreening,
)
from app.models.rbac import Role, User, UserRole
from app.models.visitor import VisitorRequest
from app.models.workflow import Notification
from app.schemas.emergency import (
    ContactTraceCreate,
    EmergencyResolve,
    EmergencyTrigger,
    HealthScreeningCreate,
    MusterUpdate,
)
from app.services.audit_service import record_audit_log
from app.services.email_service import send_bulk_email


def _generate_event_no(db: Session) -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = secrets.token_hex(2).upper()
    return f"EMG-{today}-{suffix}"


def _emails_for_roles(db: Session, role_keys: list[str]) -> list[str]:
    rows = (
        db.execute(
            select(User.email)
            .join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .where(Role.key.in_(role_keys), User.is_active.is_(True))
        )
        .scalars()
        .all()
    )
    return [r for r in rows if r]


def trigger_emergency(
    db: Session,
    payload: EmergencyTrigger,
    actor: User,
) -> EmergencyEvent:
    event = EmergencyEvent(
        event_no=_generate_event_no(db),
        event_type=payload.event_type,
        severity=payload.severity,
        status=EmergencyStatus.ACTIVE,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        triggered_at=datetime.now(timezone.utc),
        triggered_by_user_id=actor.id,
    )
    db.add(event)
    db.flush()

    # Snapshot every visitor currently checked-in into evacuation_musters.
    checked_in = (
        db.execute(
            select(VisitorRequest)
            .options(selectinload(VisitorRequest.host_user))
            .where(VisitorRequest.status == VisitorRequestStatus.CHECKED_IN)
        )
        .scalars()
        .all()
    )
    for vr in checked_in:
        muster = EvacuationMuster(
            emergency_event_id=event.id,
            visitor_request_id=vr.id,
            visitor_name_snapshot=vr.visitor_name,
            host_name_snapshot=vr.host_user.full_name if vr.host_user else None,
            status=MusterStatus.PENDING,
        )
        db.add(muster)
    db.flush()

    record_audit_log(
        db,
        entity_type="EmergencyEvent",
        entity_id=event.id,
        action="emergency.trigger",
        actor_user_id=actor.id,
        details={
            "event_type": payload.event_type.value,
            "severity": payload.severity.value,
            "musters_seeded": len(checked_in),
        },
    )

    # Fire-and-forget alert email to security/admin/gatekeeper.
    recipients = _emails_for_roles(
        db, [RoleKey.SECURITY.value, RoleKey.ADMIN.value, RoleKey.GATEKEEPER.value]
    )
    subject = f"[EMERGENCY] {payload.severity.value.upper()} {payload.event_type.value} — {payload.title}"
    text = "\n".join(
        [
            f"Event: {event.event_no}",
            f"Type: {payload.event_type.value}",
            f"Severity: {payload.severity.value}",
            f"Location: {payload.location or '-'}",
            f"Description: {payload.description or '-'}",
            f"Visitors on campus at trigger: {len(checked_in)}",
            "",
            "Open the VMS Emergency console immediately to begin muster tracking.",
        ]
    )
    html = (
        f"<h2 style='color:#b91c1c'>EMERGENCY: {payload.event_type.value.upper()}</h2>"
        f"<p><strong>{event.event_no}</strong> — {payload.title}</p>"
        f"<table border='1' cellpadding='6' cellspacing='0'>"
        f"<tr><th align='left'>Severity</th><td>{payload.severity.value}</td></tr>"
        f"<tr><th align='left'>Location</th><td>{payload.location or '-'}</td></tr>"
        f"<tr><th align='left'>Visitors on campus</th><td>{len(checked_in)}</td></tr>"
        "</table>"
        f"<p>Description: {payload.description or '-'}</p>"
        "<p><strong>Open the VMS Emergency console to begin muster tracking.</strong></p>"
    )
    send_bulk_email(
        db,
        event_type="emergency_alert",
        recipients=recipients,
        subject=subject,
        text_body=text,
        html_body=html,
        payload={
            "event_id": event.id,
            "event_no": event.event_no,
            "musters": len(checked_in),
        },
    )

    return event


def list_events(
    db: Session,
    *,
    status_filter: EmergencyStatus | None = None,
) -> list[EmergencyEvent]:
    stmt = (
        select(EmergencyEvent)
        .options(selectinload(EmergencyEvent.triggered_by))
        .order_by(EmergencyEvent.triggered_at.desc())
    )
    if status_filter:
        stmt = stmt.where(EmergencyEvent.status == status_filter)
    return list(db.execute(stmt).scalars().all())


def get_event_or_404(db: Session, event_id: int) -> EmergencyEvent:
    obj = db.get(EmergencyEvent, event_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Emergency event not found")
    return obj


def get_event_with_musters(db: Session, event_id: int) -> EmergencyEvent:
    obj = (
        db.execute(
            select(EmergencyEvent)
            .options(
                selectinload(EmergencyEvent.musters).selectinload(EvacuationMuster.accounted_by),
                selectinload(EmergencyEvent.triggered_by),
                selectinload(EmergencyEvent.resolved_by),
            )
            .where(EmergencyEvent.id == event_id)
        )
        .scalar_one_or_none()
    )
    if obj is None:
        raise HTTPException(status_code=404, detail="Emergency event not found")
    return obj


def update_muster(
    db: Session,
    muster: EvacuationMuster,
    payload: MusterUpdate,
    actor: User,
) -> EvacuationMuster:
    muster.status = payload.status
    if payload.notes is not None:
        muster.notes = payload.notes
    muster.accounted_by_user_id = actor.id
    muster.accounted_at = datetime.now(timezone.utc)
    db.flush()
    return muster


def get_muster_or_404(db: Session, muster_id: int) -> EvacuationMuster:
    obj = db.get(EvacuationMuster, muster_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Muster row not found")
    return obj


def resolve_event(
    db: Session,
    event: EmergencyEvent,
    payload: EmergencyResolve,
    actor: User,
) -> EmergencyEvent:
    if event.status == EmergencyStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="Event is already resolved")
    event.status = EmergencyStatus.RESOLVED
    event.resolved_at = datetime.now(timezone.utc)
    event.resolved_by_user_id = actor.id
    if payload.resolution_notes is not None:
        event.resolution_notes = payload.resolution_notes
    db.flush()

    record_audit_log(
        db,
        entity_type="EmergencyEvent",
        entity_id=event.id,
        action="emergency.resolve",
        actor_user_id=actor.id,
        details={"resolution_notes": payload.resolution_notes},
    )
    return event


def event_summary(db: Session, event: EmergencyEvent) -> dict:
    """Headcount summary by status for one event."""
    rows = (
        db.execute(
            select(EvacuationMuster.status, func.count(EvacuationMuster.id))
            .where(EvacuationMuster.emergency_event_id == event.id)
            .group_by(EvacuationMuster.status)
        )
        .all()
    )
    counts = {s.value: 0 for s in MusterStatus}
    for st, c in rows:
        counts[st.value if hasattr(st, "value") else str(st)] = int(c)
    return counts


# ---------- Health Screening ----------
def create_health_screening(
    db: Session, payload: HealthScreeningCreate, actor: User
) -> HealthScreening:
    if db.get(VisitorRequest, payload.visitor_request_id) is None:
        raise HTTPException(status_code=404, detail="Visitor request not found")
    record = HealthScreening(
        visitor_request_id=payload.visitor_request_id,
        temperature_celsius=payload.temperature_celsius,
        has_symptoms=payload.has_symptoms,
        symptom_notes=payload.symptom_notes,
        cleared=payload.cleared,
        screened_by_user_id=actor.id,
    )
    db.add(record)
    db.flush()
    return record


def list_health_screenings(
    db: Session, *, visitor_request_id: int | None = None
) -> list[HealthScreening]:
    stmt = (
        select(HealthScreening)
        .options(selectinload(HealthScreening.screened_by))
        .order_by(HealthScreening.created_at.desc())
    )
    if visitor_request_id is not None:
        stmt = stmt.where(HealthScreening.visitor_request_id == visitor_request_id)
    return list(db.execute(stmt).scalars().all())


# ---------- Contact Trace ----------
def create_contact_trace(
    db: Session, payload: ContactTraceCreate, actor: User
) -> ContactTraceRecord:
    if db.get(VisitorRequest, payload.source_visitor_request_id) is None:
        raise HTTPException(status_code=404, detail="Source visitor request not found")
    record = ContactTraceRecord(
        source_visitor_request_id=payload.source_visitor_request_id,
        contact_visitor_request_id=payload.contact_visitor_request_id,
        contact_user_id=payload.contact_user_id,
        contact_name=payload.contact_name,
        location=payload.location,
        contact_at=payload.contact_at,
        notes=payload.notes,
        recorded_by_user_id=actor.id,
    )
    db.add(record)
    db.flush()
    return record


def list_contact_traces(
    db: Session, *, source_visitor_request_id: int | None = None
) -> list[ContactTraceRecord]:
    stmt = select(ContactTraceRecord).order_by(ContactTraceRecord.created_at.desc())
    if source_visitor_request_id is not None:
        stmt = stmt.where(ContactTraceRecord.source_visitor_request_id == source_visitor_request_id)
    return list(db.execute(stmt).scalars().all())
