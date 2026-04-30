from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import NotificationChannel, NotificationStatus
from app.models.workflow import Notification


def queue_notifications(
    db: Session,
    *,
    recipient_user_ids: list[int],
    event_type: str,
    title: str,
    message: str,
    payload: dict | None = None,
) -> list[Notification]:
    notifications: list[Notification] = []
    for user_id in recipient_user_ids:
        notification = Notification(
            recipient_user_id=user_id,
            channel=NotificationChannel.SYSTEM,
            event_type=event_type,
            title=title,
            message=message,
            status=NotificationStatus.PENDING,
            payload_json=payload or {},
        )
        db.add(notification)
        notifications.append(notification)
    db.flush()
    return notifications

