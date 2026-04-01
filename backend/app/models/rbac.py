from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import RoleKey
from app.db.base_class import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.visitor import Attachment, InterviewPanelMember, VisitorDocument, VisitorLog, VisitorRequest
    from app.models.workflow import ApprovalAction, ApprovalStep, AuditLog, Notification, VisitorBlacklist


class Department(TimestampMixin, Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str | None] = mapped_column(Text())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    users: Mapped[list["User"]] = relationship(back_populates="department")
    requests: Mapped[list["VisitorRequest"]] = relationship(back_populates="department")


class UserRole(TimestampMixin, Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)

    user: Mapped["User"] = relationship(back_populates="role_assignments")
    role: Mapped["Role"] = relationship(back_populates="user_assignments")


class Role(TimestampMixin, Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text())
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)

    user_assignments: Mapped[list[UserRole]] = relationship(back_populates="role", cascade="all, delete-orphan")
    users: Mapped[list["User"]] = relationship(secondary="user_roles", back_populates="roles", viewonly=True)

    @property
    def role_key(self) -> RoleKey | str:
        try:
            return RoleKey(self.key)
        except ValueError:
            return self.key


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_code: Mapped[str | None] = mapped_column(String(40), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    mobile: Mapped[str | None] = mapped_column(String(20))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))

    department: Mapped[Department | None] = relationship(back_populates="users")
    role_assignments: Mapped[list[UserRole]] = relationship(back_populates="user", cascade="all, delete-orphan")
    roles: Mapped[list[Role]] = relationship(secondary="user_roles", back_populates="users", viewonly=True)

    requested_visits: Mapped[list["VisitorRequest"]] = relationship(
        back_populates="requested_by", foreign_keys="VisitorRequest.requested_by_user_id"
    )
    hosted_visits: Mapped[list["VisitorRequest"]] = relationship(
        back_populates="host_user", foreign_keys="VisitorRequest.host_user_id"
    )
    uploaded_documents: Mapped[list["VisitorDocument"]] = relationship(back_populates="uploaded_by")
    uploaded_attachments: Mapped[list["Attachment"]] = relationship(back_populates="uploaded_by")
    approval_steps: Mapped[list["ApprovalStep"]] = relationship(back_populates="assigned_user")
    approval_actions: Mapped[list["ApprovalAction"]] = relationship(back_populates="action_by")
    visitor_logs: Mapped[list["VisitorLog"]] = relationship(back_populates="performed_by")
    blacklist_entries: Mapped[list["VisitorBlacklist"]] = relationship(back_populates="added_by")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="recipient")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="actor")
    interview_panels: Mapped[list["InterviewPanelMember"]] = relationship(back_populates="panel_member")

