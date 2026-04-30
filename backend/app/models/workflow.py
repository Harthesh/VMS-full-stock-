from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    ApprovalActionType,
    ApprovalStepStatus,
    BlacklistActionType,
    NotificationChannel,
    NotificationStatus,
)
from app.db.base_class import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.rbac import User
    from app.models.visitor import VisitorRequest


def enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class ApprovalStep(TimestampMixin, Base):
    __tablename__ = "approval_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_request_id: Mapped[int] = mapped_column(ForeignKey("visitor_requests.id", ondelete="CASCADE"), index=True)
    step_order: Mapped[int] = mapped_column(Integer, index=True)
    step_key: Mapped[str] = mapped_column(String(80))
    step_name: Mapped[str] = mapped_column(String(120))
    role_key: Mapped[str] = mapped_column(String(50), index=True)
    assigned_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    pending_status: Mapped[str] = mapped_column(String(80))
    status: Mapped[ApprovalStepStatus] = mapped_column(
        Enum(ApprovalStepStatus, name="approval_step_status_enum", values_callable=enum_values),
        default=ApprovalStepStatus.QUEUED,
    )
    remarks: Mapped[str | None] = mapped_column(Text())

    visitor_request: Mapped["VisitorRequest"] = relationship(back_populates="approval_steps")
    assigned_user: Mapped["User"] = relationship(back_populates="approval_steps")
    actions: Mapped[list["ApprovalAction"]] = relationship(back_populates="approval_step", cascade="all, delete-orphan")


class ApprovalAction(TimestampMixin, Base):
    __tablename__ = "approval_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_request_id: Mapped[int] = mapped_column(ForeignKey("visitor_requests.id", ondelete="CASCADE"), index=True)
    approval_step_id: Mapped[int | None] = mapped_column(ForeignKey("approval_steps.id", ondelete="SET NULL"))
    action: Mapped[ApprovalActionType] = mapped_column(
        Enum(ApprovalActionType, name="approval_action_type_enum", values_callable=enum_values)
    )
    action_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    remarks: Mapped[str | None] = mapped_column(Text())
    from_status: Mapped[str | None] = mapped_column(String(80))
    to_status: Mapped[str | None] = mapped_column(String(80))

    visitor_request: Mapped["VisitorRequest"] = relationship(back_populates="approval_actions")
    approval_step: Mapped[ApprovalStep | None] = relationship(back_populates="actions")
    action_by: Mapped["User"] = relationship(back_populates="approval_actions")


class VisitorBlacklist(TimestampMixin, Base):
    __tablename__ = "visitor_blacklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_name: Mapped[str] = mapped_column(String(120), index=True)
    mobile: Mapped[str | None] = mapped_column(String(20), index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    id_proof_type: Mapped[str | None] = mapped_column(String(80))
    id_proof_number: Mapped[str | None] = mapped_column(String(80), index=True)
    reason: Mapped[str] = mapped_column(Text())
    action_type: Mapped[BlacklistActionType] = mapped_column(
        Enum(BlacklistActionType, name="blacklist_action_type_enum", values_callable=enum_values),
        default=BlacklistActionType.BLOCK,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    added_by: Mapped["User"] = relationship(back_populates="blacklist_entries")


class Notification(TimestampMixin, Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipient_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, name="notification_channel_enum", values_callable=enum_values),
        default=NotificationChannel.SYSTEM,
    )
    event_type: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(160))
    message: Mapped[str] = mapped_column(Text())
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, name="notification_status_enum", values_callable=enum_values),
        default=NotificationStatus.PENDING,
    )
    payload_json: Mapped[dict | None] = mapped_column(JSON)

    recipient: Mapped["User"] = relationship(back_populates="notifications")


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[int] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    details_json: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(64))

    actor: Mapped["User"] = relationship(back_populates="audit_logs")


class AppSetting(TimestampMixin, Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text())
    value_type: Mapped[str] = mapped_column(String(40), default="string")
    description: Mapped[str | None] = mapped_column(Text())
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
