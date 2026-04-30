from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import (
    EmergencySeverity,
    EmergencyStatus,
    EmergencyType,
    MusterStatus,
)
from app.db.base_class import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.rbac import User
    from app.models.visitor import VisitorRequest


def enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class EmergencyEvent(TimestampMixin, Base):
    __tablename__ = "emergency_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_no: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    event_type: Mapped[EmergencyType] = mapped_column(
        Enum(EmergencyType, name="emergency_type_enum", values_callable=enum_values),
        index=True,
    )
    severity: Mapped[EmergencySeverity] = mapped_column(
        Enum(EmergencySeverity, name="emergency_severity_enum", values_callable=enum_values),
        default=EmergencySeverity.MEDIUM,
    )
    status: Mapped[EmergencyStatus] = mapped_column(
        Enum(EmergencyStatus, name="emergency_status_enum", values_callable=enum_values),
        default=EmergencyStatus.ACTIVE,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text())
    location: Mapped[str | None] = mapped_column(String(200))
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    triggered_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    resolved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    resolution_notes: Mapped[str | None] = mapped_column(Text())

    triggered_by: Mapped["User"] = relationship(foreign_keys=[triggered_by_user_id])
    resolved_by: Mapped["User"] = relationship(foreign_keys=[resolved_by_user_id])
    musters: Mapped[list["EvacuationMuster"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class EvacuationMuster(TimestampMixin, Base):
    __tablename__ = "evacuation_musters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emergency_event_id: Mapped[int] = mapped_column(
        ForeignKey("emergency_events.id", ondelete="CASCADE"), index=True
    )
    visitor_request_id: Mapped[int] = mapped_column(
        ForeignKey("visitor_requests.id", ondelete="CASCADE"), index=True
    )
    visitor_name_snapshot: Mapped[str] = mapped_column(String(120))
    host_name_snapshot: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[MusterStatus] = mapped_column(
        Enum(MusterStatus, name="muster_status_enum", values_callable=enum_values),
        default=MusterStatus.PENDING,
        index=True,
    )
    accounted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accounted_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    notes: Mapped[str | None] = mapped_column(Text())

    event: Mapped[EmergencyEvent] = relationship(back_populates="musters")
    visitor_request: Mapped["VisitorRequest"] = relationship()
    accounted_by: Mapped["User"] = relationship()


class HealthScreening(TimestampMixin, Base):
    __tablename__ = "health_screenings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    visitor_request_id: Mapped[int] = mapped_column(
        ForeignKey("visitor_requests.id", ondelete="CASCADE"), index=True
    )
    temperature_celsius: Mapped[float | None] = mapped_column(Float)
    has_symptoms: Mapped[bool] = mapped_column(default=False)
    symptom_notes: Mapped[str | None] = mapped_column(Text())
    cleared: Mapped[bool] = mapped_column(default=True)
    screened_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    visitor_request: Mapped["VisitorRequest"] = relationship()
    screened_by: Mapped["User"] = relationship()


class ContactTraceRecord(TimestampMixin, Base):
    __tablename__ = "contact_trace_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_visitor_request_id: Mapped[int] = mapped_column(
        ForeignKey("visitor_requests.id", ondelete="CASCADE"), index=True
    )
    contact_visitor_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("visitor_requests.id", ondelete="SET NULL"), index=True
    )
    contact_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    contact_name: Mapped[str | None] = mapped_column(String(120))
    location: Mapped[str | None] = mapped_column(String(200))
    contact_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text())
    recorded_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    source_visitor_request: Mapped["VisitorRequest"] = relationship(
        foreign_keys=[source_visitor_request_id]
    )
    contact_visitor_request: Mapped["VisitorRequest"] = relationship(
        foreign_keys=[contact_visitor_request_id]
    )
    contact_user: Mapped["User"] = relationship(foreign_keys=[contact_user_id])
    recorded_by: Mapped["User"] = relationship(foreign_keys=[recorded_by_user_id])
