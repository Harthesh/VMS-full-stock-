from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.core.enums import ApprovalActionType, ApprovalStepStatus
from app.schemas.common import ORMBaseModel
from app.schemas.user import UserSummary


class ApprovalStepRead(ORMBaseModel):
    id: int
    step_order: int
    step_key: str
    step_name: str
    role_key: str
    pending_status: str
    status: ApprovalStepStatus
    assigned_user: UserSummary | None = None
    remarks: str | None = None


class ApprovalActionRead(ORMBaseModel):
    id: int
    action: ApprovalActionType
    remarks: str | None = None
    from_status: str | None = None
    to_status: str | None = None
    action_by: UserSummary | None = None
    created_at: datetime


class ApprovalActionCreate(BaseModel):
    action: ApprovalActionType
    remarks: str | None = None


class PendingApprovalItem(ORMBaseModel):
    request_id: int
    request_no: str
    visitor_name: str
    visitor_type: str
    visit_date: date | None = None
    status: str
    current_step: ApprovalStepRead
