from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import RoleKey
from app.models.rbac import User
from app.models.visitor import HospitalityRequest, VisitorRequest
from app.schemas.hospitality import HospitalityUpdate
from app.services.audit_service import record_audit_log
from app.services.email_service import send_hospitality_status_email

ALLOWED_STATUSES = {"pending", "in_progress", "completed", "cancelled"}


def _has_role(user: User, role_key: str) -> bool:
    return any(r.key == role_key for r in user.roles)


def _can_manage(user: User) -> bool:
    return _has_role(user, RoleKey.ADMIN.value) or _has_role(user, RoleKey.HR.value)


def list_hospitality(
    db: Session,
    current_user: User,
    *,
    status_filter: str | None = None,
    visit_date: date | None = None,
) -> list[HospitalityRequest]:
    stmt = (
        select(HospitalityRequest)
        .join(VisitorRequest, VisitorRequest.id == HospitalityRequest.visitor_request_id)
        .options(
            selectinload(HospitalityRequest.visitor_request).selectinload(VisitorRequest.host_user)
        )
        .order_by(VisitorRequest.visit_date.desc(), VisitorRequest.visit_time.asc().nullslast())
    )
    if status_filter:
        stmt = stmt.where(HospitalityRequest.logistics_status == status_filter)
    if visit_date is not None:
        stmt = stmt.where(VisitorRequest.visit_date == visit_date)

    if not _can_manage(current_user):
        # Non-managers see only the requests they host or requested.
        stmt = stmt.where(
            (VisitorRequest.host_user_id == current_user.id)
            | (VisitorRequest.requested_by_user_id == current_user.id)
        )

    return list(db.execute(stmt).scalars().all())


def get_hospitality_or_404(db: Session, hospitality_id: int) -> HospitalityRequest:
    obj = db.get(HospitalityRequest, hospitality_id)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospitality request not found")
    # Eager load relationship if not already loaded
    db.refresh(obj)
    return obj


def update_hospitality(
    db: Session,
    hospitality: HospitalityRequest,
    payload: HospitalityUpdate,
    current_user: User,
) -> HospitalityRequest:
    if not _can_manage(current_user):
        # Allow the host of the visit to view/edit too.
        vr = hospitality.visitor_request
        if vr.host_user_id != current_user.id and vr.requested_by_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

    data = payload.model_dump(exclude_unset=True)
    if "logistics_status" in data and data["logistics_status"] not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"logistics_status must be one of {sorted(ALLOWED_STATUSES)}",
        )

    previous = {k: getattr(hospitality, k) for k in data.keys() if hasattr(hospitality, k)}
    for key, value in data.items():
        setattr(hospitality, key, value)
    db.flush()

    record_audit_log(
        db,
        entity_type="HospitalityRequest",
        entity_id=hospitality.id,
        action="hospitality.update",
        actor_user_id=current_user.id,
        details={"previous": previous, "next": data},
    )

    if "logistics_status" in data and data["logistics_status"] != previous.get("logistics_status"):
        send_hospitality_status_email(db, hospitality, data["logistics_status"])

    return hospitality
