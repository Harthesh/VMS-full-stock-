from __future__ import annotations

from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import InvitationStatus, VisitorType
from app.db.base_class import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.rbac import User
    from app.models.visitor import VisitorRequest


def enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class VisitorInvitation(TimestampMixin, Base):
    __tablename__ = "visitor_invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    host_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))

    visitor_name: Mapped[str] = mapped_column(String(120))
    visitor_email: Mapped[str | None] = mapped_column(String(255))
    visitor_mobile: Mapped[str | None] = mapped_column(String(20))
    company_name: Mapped[str | None] = mapped_column(String(160))
    visitor_type: Mapped[VisitorType] = mapped_column(
        Enum(
            VisitorType,
            name="visitor_type_enum",
            create_type=False,
            _create_events=False,
            values_callable=enum_values,
        ),
    )
    visit_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    visit_time: Mapped[time | None] = mapped_column(Time())
    purpose: Mapped[str] = mapped_column(Text())

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[InvitationStatus] = mapped_column(
        Enum(InvitationStatus, name="invitation_status_enum", values_callable=enum_values),
        default=InvitationStatus.PENDING,
        index=True,
    )
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    visitor_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("visitor_requests.id", ondelete="SET NULL")
    )

    host: Mapped["User"] = relationship()
    visitor_request: Mapped["VisitorRequest"] = relationship()
