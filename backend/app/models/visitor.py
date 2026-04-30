from __future__ import annotations

from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import BadgeStatus, GateAction, VisitorRequestStatus, VisitorType
from app.db.base_class import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.rbac import Department, User
    from app.models.workflow import ApprovalAction, ApprovalStep


def enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class VisitorRequest(TimestampMixin, Base):
    __tablename__ = "visitor_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    visitor_type: Mapped[VisitorType] = mapped_column(
        Enum(VisitorType, name="visitor_type_enum", values_callable=enum_values),
        index=True,
    )
    request_date: Mapped[date] = mapped_column(Date, nullable=False)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    visit_time: Mapped[time | None] = mapped_column(Time())
    requested_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))
    host_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    visitor_name: Mapped[str] = mapped_column(String(120), index=True)
    company_name: Mapped[str | None] = mapped_column(String(160))
    mobile: Mapped[str] = mapped_column(String(20), index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    id_proof_type: Mapped[str | None] = mapped_column(String(80))
    id_proof_number: Mapped[str | None] = mapped_column(String(80), index=True)
    purpose: Mapped[str] = mapped_column(Text())
    status: Mapped[VisitorRequestStatus] = mapped_column(
        Enum(VisitorRequestStatus, name="visitor_request_status_enum", values_callable=enum_values),
        default=VisitorRequestStatus.DRAFT,
        index=True,
    )
    current_approval_level: Mapped[int] = mapped_column(Integer, default=0)
    requires_security_clearance: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_it_access: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_hospitality: Mapped[bool] = mapped_column(Boolean, default=False)
    remarks: Mapped[str | None] = mapped_column(Text())
    badge_no: Mapped[str | None] = mapped_column(String(40), unique=True)
    qr_code_value: Mapped[str | None] = mapped_column(String(120), unique=True)
    is_id_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    check_in_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    check_out_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    requested_by: Mapped["User"] = relationship(back_populates="requested_visits", foreign_keys=[requested_by_user_id])
    host_user: Mapped["User"] = relationship(back_populates="hosted_visits", foreign_keys=[host_user_id])
    department: Mapped["Department"] = relationship(back_populates="requests")
    documents: Mapped[list["VisitorDocument"]] = relationship(back_populates="visitor_request", cascade="all, delete-orphan")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="visitor_request", cascade="all, delete-orphan")
    approval_steps: Mapped[list["ApprovalStep"]] = relationship(back_populates="visitor_request", cascade="all, delete-orphan")
    approval_actions: Mapped[list["ApprovalAction"]] = relationship(
        back_populates="visitor_request", cascade="all, delete-orphan"
    )
    badge: Mapped["VisitorBadge"] = relationship(back_populates="visitor_request", cascade="all, delete-orphan")
    logs: Mapped[list["VisitorLog"]] = relationship(back_populates="visitor_request", cascade="all, delete-orphan")
    hospitality_request: Mapped["HospitalityRequest"] = relationship(
        back_populates="visitor_request", cascade="all, delete-orphan"
    )
    interview_panels: Mapped[list["InterviewPanelMember"]] = relationship(
        back_populates="visitor_request", cascade="all, delete-orphan"
    )


class VisitorDocument(TimestampMixin, Base):
    __tablename__ = "visitor_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_request_id: Mapped[int] = mapped_column(ForeignKey("visitor_requests.id", ondelete="CASCADE"))
    document_type: Mapped[str] = mapped_column(String(80))
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str | None] = mapped_column(String(120))
    uploaded_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    visitor_request: Mapped[VisitorRequest] = relationship(back_populates="documents")
    uploaded_by: Mapped["User"] = relationship(back_populates="uploaded_documents")


class Attachment(TimestampMixin, Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[int] = mapped_column(Integer, index=True)
    visitor_request_id: Mapped[int | None] = mapped_column(ForeignKey("visitor_requests.id", ondelete="CASCADE"))
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str | None] = mapped_column(String(120))
    uploaded_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    visitor_request: Mapped[VisitorRequest | None] = relationship(back_populates="attachments")
    uploaded_by: Mapped["User"] = relationship(back_populates="uploaded_attachments")


class VisitorBadge(TimestampMixin, Base):
    __tablename__ = "visitor_badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_request_id: Mapped[int] = mapped_column(ForeignKey("visitor_requests.id", ondelete="CASCADE"), unique=True)
    badge_no: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    qr_code_value: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    status: Mapped[BadgeStatus] = mapped_column(
        Enum(BadgeStatus, name="badge_status_enum", values_callable=enum_values),
        default=BadgeStatus.GENERATED,
    )
    printed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    visitor_request: Mapped[VisitorRequest] = relationship(back_populates="badge")


class VisitorLog(TimestampMixin, Base):
    __tablename__ = "visitor_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_request_id: Mapped[int] = mapped_column(ForeignKey("visitor_requests.id", ondelete="CASCADE"), index=True)
    action: Mapped[GateAction] = mapped_column(
        Enum(GateAction, name="gate_action_enum", values_callable=enum_values),
        index=True,
    )
    gate_entry_point: Mapped[str | None] = mapped_column(String(120))
    remarks: Mapped[str | None] = mapped_column(Text())
    performed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    visitor_request: Mapped[VisitorRequest] = relationship(back_populates="logs")
    performed_by: Mapped["User"] = relationship(back_populates="visitor_logs")


class VisitorZone(TimestampMixin, Base):
    __tablename__ = "visitor_zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str | None] = mapped_column(Text())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class HospitalityRequest(TimestampMixin, Base):
    __tablename__ = "hospitality_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_request_id: Mapped[int] = mapped_column(ForeignKey("visitor_requests.id", ondelete="CASCADE"), unique=True)
    meal_required: Mapped[bool] = mapped_column(Boolean, default=False)
    transport_required: Mapped[bool] = mapped_column(Boolean, default=False)
    meeting_room: Mapped[str | None] = mapped_column(String(120))
    escort_needed: Mapped[bool] = mapped_column(Boolean, default=False)
    vip_notes: Mapped[str | None] = mapped_column(Text())
    logistics_status: Mapped[str] = mapped_column(String(50), default="pending")
    remarks: Mapped[str | None] = mapped_column(Text())

    visitor_request: Mapped[VisitorRequest] = relationship(back_populates="hospitality_request")


class InterviewPanelMember(TimestampMixin, Base):
    __tablename__ = "interview_panel_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_request_id: Mapped[int] = mapped_column(ForeignKey("visitor_requests.id", ondelete="CASCADE"), index=True)
    panel_member_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    notes: Mapped[str | None] = mapped_column(Text())

    visitor_request: Mapped[VisitorRequest] = relationship(back_populates="interview_panels")
    panel_member: Mapped["User"] = relationship(back_populates="interview_panels")
