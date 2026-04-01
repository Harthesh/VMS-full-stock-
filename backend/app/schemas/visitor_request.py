from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel, EmailStr, Field

from app.core.enums import BadgeStatus, VisitorRequestStatus, VisitorType
from app.schemas.approval import ApprovalActionRead, ApprovalStepRead
from app.schemas.common import ORMBaseModel
from app.schemas.user import DepartmentBase, UserSummary


class HospitalityRequestInput(BaseModel):
    meal_required: bool = False
    transport_required: bool = False
    meeting_room: str | None = None
    escort_needed: bool = False
    vip_notes: str | None = None
    remarks: str | None = None


class HospitalityRequestRead(ORMBaseModel):
    id: int
    meal_required: bool
    transport_required: bool
    meeting_room: str | None = None
    escort_needed: bool
    vip_notes: str | None = None
    logistics_status: str
    remarks: str | None = None


class VisitorBadgeRead(ORMBaseModel):
    id: int
    badge_no: str
    qr_code_value: str
    status: BadgeStatus


class VisitorDocumentRead(ORMBaseModel):
    id: int
    document_type: str
    file_name: str
    file_path: str
    content_type: str | None = None


class VisitorRequestBase(BaseModel):
    visitor_type: VisitorType
    visit_date: date
    visit_time: time | None = None
    department_id: int | None = None
    host_user_id: int | None = None
    visitor_name: str
    company_name: str | None = None
    mobile: str
    email: EmailStr | None = None
    id_proof_type: str | None = None
    id_proof_number: str | None = None
    purpose: str
    requires_security_clearance: bool = False
    requires_it_access: bool = False
    requires_hospitality: bool = False
    remarks: str | None = None
    hospitality: HospitalityRequestInput | None = None
    panel_member_user_ids: list[int] = Field(default_factory=list)


class VisitorRequestCreate(VisitorRequestBase):
    pass


class VisitorRequestUpdate(BaseModel):
    visit_date: date | None = None
    visit_time: time | None = None
    department_id: int | None = None
    host_user_id: int | None = None
    visitor_name: str | None = None
    company_name: str | None = None
    mobile: str | None = None
    email: EmailStr | None = None
    id_proof_type: str | None = None
    id_proof_number: str | None = None
    purpose: str | None = None
    requires_security_clearance: bool | None = None
    requires_it_access: bool | None = None
    requires_hospitality: bool | None = None
    remarks: str | None = None
    hospitality: HospitalityRequestInput | None = None
    panel_member_user_ids: list[int] | None = None


class VisitorRequestListItem(ORMBaseModel):
    id: int
    request_no: str
    visitor_type: VisitorType
    visit_date: date
    visitor_name: str
    company_name: str | None = None
    status: VisitorRequestStatus
    badge_no: str | None = None
    requested_by: UserSummary
    host_user: UserSummary | None = None


class VisitorRequestRead(VisitorRequestListItem):
    request_date: date
    visit_time: time | None = None
    department: DepartmentBase | None = None
    mobile: str
    email: EmailStr | None = None
    id_proof_type: str | None = None
    id_proof_number: str | None = None
    purpose: str
    current_approval_level: int
    requires_security_clearance: bool
    requires_it_access: bool
    requires_hospitality: bool
    remarks: str | None = None
    qr_code_value: str | None = None
    is_id_verified: bool
    check_in_time: datetime | None = None
    check_out_time: datetime | None = None
    hospitality_request: HospitalityRequestRead | None = None
    badge: VisitorBadgeRead | None = None
    documents: list[VisitorDocumentRead] = []
    approval_steps: list[ApprovalStepRead] = []
    approval_actions: list[ApprovalActionRead] = []

