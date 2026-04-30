from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.enums import NotificationStatus, RoleKey
from app.db.session import get_db
from app.models.rbac import User
from app.models.workflow import Notification
from app.schemas.notification import NotificationRead

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NotificationRead]:
    statement = select(Notification).order_by(Notification.created_at.desc())
    user_role_keys = {role.key for role in current_user.roles}
    if RoleKey.ADMIN.value not in user_role_keys:
      statement = statement.where(Notification.recipient_user_id == current_user.id)
    return list(db.execute(statement.limit(100)).scalars().all())


@router.post("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationRead:
    notification = db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    if notification.recipient_user_id not in {None, current_user.id} and all(role.key != RoleKey.ADMIN.value for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot update this notification")
    notification.status = NotificationStatus.READ
    db.commit()
    db.refresh(notification)
    return notification

