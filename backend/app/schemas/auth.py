from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.schemas.user import RoleRead


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "CurrentUserResponse"


class CurrentUserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    department_id: int | None = None
    roles: list[RoleRead]


TokenResponse.model_rebuild()

