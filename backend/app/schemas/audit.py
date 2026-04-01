from __future__ import annotations

from datetime import datetime

from app.schemas.common import ORMBaseModel


class AuditLogRead(ORMBaseModel):
    id: int
    entity_type: str
    entity_id: int
    action: str
    actor_user_id: int | None = None
    details_json: dict | None = None
    ip_address: str | None = None
    created_at: datetime

