from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.enums import BadgeStatus
from app.models.visitor import VisitorBadge, VisitorRequest


def ensure_badge(db: Session, visitor_request: VisitorRequest) -> VisitorBadge:
    if visitor_request.badge:
        return visitor_request.badge

    badge = VisitorBadge(
        visitor_request=visitor_request,
        badge_no=visitor_request.badge_no or f"BADGE-{visitor_request.id:06d}",
        qr_code_value=visitor_request.qr_code_value or f"VMS:{visitor_request.request_no}:{uuid4().hex[:12]}",
        status=BadgeStatus.GENERATED,
    )
    visitor_request.badge_no = badge.badge_no
    visitor_request.qr_code_value = badge.qr_code_value
    db.add(badge)
    db.flush()
    return badge

