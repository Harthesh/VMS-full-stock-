from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.workflow import AuditLog


def record_audit_log(
    db: Session,
    *,
    entity_type: str,
    entity_id: int,
    action: str,
    actor_user_id: int | None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor_user_id=actor_user_id,
        details_json=details or {},
        ip_address=ip_address,
    )
    db.add(entry)
    db.flush()
    return entry

