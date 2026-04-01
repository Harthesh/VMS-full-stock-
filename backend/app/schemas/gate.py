from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.core.enums import BlacklistActionType
from app.schemas.user import UserSummary
from app.schemas.visitor_request import VisitorBadgeRead, VisitorRequestRead


class GateLookupRequest(BaseModel):
    qr_code_value: str | None = None
    request_no: str | None = None
    visitor_name: str | None = None
    mobile: str | None = None


class GateLookupResponse(BaseModel):
    request: VisitorRequestRead
    badge: VisitorBadgeRead | None = None
    host: UserSummary | None = None
    blacklist_action: BlacklistActionType | None = None
    blacklist_reason: str | None = None
    can_check_in: bool
    can_check_out: bool


class GateActionPayload(BaseModel):
    gate_entry_point: str | None = None
    remarks: str | None = None


class GateActionResponse(BaseModel):
    request_id: int
    status: str
    check_in_time: datetime | None = None
    check_out_time: datetime | None = None
    remarks: str | None = None

