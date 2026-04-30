from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel, EmailStr

from app.core.enums import InvitationStatus, VisitorType
from app.schemas.common import ORMBaseModel
from app.schemas.user import UserSummary


class InvitationCreate(BaseModel):
    visitor_name: str
    visitor_email: EmailStr | None = None
    visitor_mobile: str | None = None
    company_name: str | None = None
    visitor_type: VisitorType = VisitorType.CUSTOMER
    visit_date: date
    visit_time: time | None = None
    purpose: str
    department_id: int | None = None
    expires_in_days: int = 7


class InvitationListItem(ORMBaseModel):
    id: int
    token: str
    visitor_name: str
    visitor_email: str | None = None
    visitor_mobile: str | None = None
    company_name: str | None = None
    visitor_type: VisitorType
    visit_date: date
    visit_time: time | None = None
    purpose: str
    expires_at: datetime
    status: InvitationStatus
    used_at: datetime | None = None
    visitor_request_id: int | None = None
    host: UserSummary
    created_at: datetime


class InvitationPublicView(BaseModel):
    """Public-safe view returned to the visitor at /invite/:token."""

    visitor_name: str
    visitor_email: str | None = None
    visitor_mobile: str | None = None
    company_name: str | None = None
    visitor_type: VisitorType
    visit_date: date
    visit_time: time | None = None
    purpose: str
    host_name: str
    host_email: str
    expires_at: datetime
    status: InvitationStatus


class InvitationPublicSubmit(BaseModel):
    """What the visitor sends back when filling the pre-registration form."""

    visitor_name: str
    visitor_email: EmailStr | None = None
    mobile: str
    company_name: str | None = None
    id_proof_type: str | None = None
    id_proof_number: str | None = None
    purpose: str | None = None
    remarks: str | None = None
