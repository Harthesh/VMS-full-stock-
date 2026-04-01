from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class VisitorSummaryRow(BaseModel):
    request_no: str
    visitor_name: str
    visitor_type: str
    visit_date: date
    status: str
    host_name: str | None = None


class DailyGateMovementRow(BaseModel):
    request_no: str
    visitor_name: str
    check_in_time: datetime | None = None
    check_out_time: datetime | None = None
    badge_no: str | None = None


class PendingApprovalRow(BaseModel):
    request_no: str
    visitor_name: str
    current_status: str
    pending_role: str
    visit_date: date


class BlacklistAlertRow(BaseModel):
    request_no: str
    visitor_name: str
    action: str
    remarks: str | None = None
    created_at: datetime


class VisitorTypeSummaryRow(BaseModel):
    visitor_type: str
    count: int

