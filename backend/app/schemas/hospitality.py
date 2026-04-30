from __future__ import annotations

from datetime import date, time
from typing import Literal

from pydantic import BaseModel

from app.schemas.common import ORMBaseModel
from app.schemas.user import UserSummary


HospitalityStatus = Literal["pending", "in_progress", "completed", "cancelled"]


class HospitalityVisitorInfo(BaseModel):
    id: int
    request_no: str
    visitor_name: str
    company_name: str | None = None
    visit_date: date
    visit_time: time | None = None
    status: str
    host_user: UserSummary | None = None

    model_config = {"from_attributes": True}


class HospitalityListItem(ORMBaseModel):
    id: int
    visitor_request_id: int
    meal_required: bool
    transport_required: bool
    meeting_room: str | None = None
    escort_needed: bool
    vip_notes: str | None = None
    logistics_status: HospitalityStatus | str
    remarks: str | None = None
    visitor_request: HospitalityVisitorInfo


class HospitalityUpdate(BaseModel):
    logistics_status: HospitalityStatus | None = None
    meal_required: bool | None = None
    transport_required: bool | None = None
    meeting_room: str | None = None
    escort_needed: bool | None = None
    vip_notes: str | None = None
    remarks: str | None = None
