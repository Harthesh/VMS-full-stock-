from __future__ import annotations

from datetime import datetime

from app.core.enums import NotificationChannel, NotificationStatus
from app.schemas.common import ORMBaseModel


class NotificationRead(ORMBaseModel):
    id: int
    channel: NotificationChannel
    event_type: str
    title: str
    message: str
    status: NotificationStatus
    payload_json: dict | None = None
    created_at: datetime

