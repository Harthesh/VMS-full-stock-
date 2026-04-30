from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.core.enums import (
    EmergencySeverity,
    EmergencyStatus,
    EmergencyType,
    MusterStatus,
)
from app.schemas.common import ORMBaseModel
from app.schemas.user import UserSummary


class EmergencyTrigger(BaseModel):
    event_type: EmergencyType
    severity: EmergencySeverity = EmergencySeverity.MEDIUM
    title: str
    description: str | None = None
    location: str | None = None


class EmergencyResolve(BaseModel):
    resolution_notes: str | None = None


class MusterUpdate(BaseModel):
    status: MusterStatus
    notes: str | None = None


class MusterRead(ORMBaseModel):
    id: int
    visitor_request_id: int
    visitor_name_snapshot: str
    host_name_snapshot: str | None = None
    status: MusterStatus
    accounted_at: datetime | None = None
    notes: str | None = None
    accounted_by: UserSummary | None = None


class EmergencyEventListItem(ORMBaseModel):
    id: int
    event_no: str
    event_type: EmergencyType
    severity: EmergencySeverity
    status: EmergencyStatus
    title: str
    location: str | None = None
    triggered_at: datetime
    resolved_at: datetime | None = None
    triggered_by: UserSummary | None = None


class EmergencyEventRead(EmergencyEventListItem):
    description: str | None = None
    resolution_notes: str | None = None
    resolved_by: UserSummary | None = None
    musters: list[MusterRead] = []


class HealthScreeningCreate(BaseModel):
    visitor_request_id: int
    temperature_celsius: float | None = None
    has_symptoms: bool = False
    symptom_notes: str | None = None
    cleared: bool = True


class HealthScreeningRead(ORMBaseModel):
    id: int
    visitor_request_id: int
    temperature_celsius: float | None = None
    has_symptoms: bool
    symptom_notes: str | None = None
    cleared: bool
    screened_by: UserSummary | None = None
    created_at: datetime


class ContactTraceCreate(BaseModel):
    source_visitor_request_id: int
    contact_visitor_request_id: int | None = None
    contact_user_id: int | None = None
    contact_name: str | None = None
    location: str | None = None
    contact_at: datetime | None = None
    notes: str | None = None


class ContactTraceRead(ORMBaseModel):
    id: int
    source_visitor_request_id: int
    contact_visitor_request_id: int | None = None
    contact_user_id: int | None = None
    contact_name: str | None = None
    location: str | None = None
    contact_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
