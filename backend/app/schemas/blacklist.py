from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.core.enums import BlacklistActionType
from app.schemas.common import ORMBaseModel
from app.schemas.user import UserSummary


class BlacklistBase(BaseModel):
    visitor_name: str
    mobile: str | None = None
    email: EmailStr | None = None
    id_proof_type: str | None = None
    id_proof_number: str | None = None
    reason: str
    action_type: BlacklistActionType = BlacklistActionType.BLOCK
    is_active: bool = True


class BlacklistCreate(BlacklistBase):
    pass


class BlacklistUpdate(BaseModel):
    visitor_name: str | None = None
    mobile: str | None = None
    email: EmailStr | None = None
    id_proof_type: str | None = None
    id_proof_number: str | None = None
    reason: str | None = None
    action_type: BlacklistActionType | None = None
    is_active: bool | None = None


class BlacklistRead(ORMBaseModel):
    id: int
    visitor_name: str
    mobile: str | None = None
    email: EmailStr | None = None
    id_proof_type: str | None = None
    id_proof_number: str | None = None
    reason: str
    action_type: BlacklistActionType
    is_active: bool
    added_by: UserSummary | None = None

