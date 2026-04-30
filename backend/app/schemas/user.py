from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.schemas.common import ORMBaseModel


class DepartmentBase(ORMBaseModel):
    id: int
    code: str
    name: str


class RoleRead(ORMBaseModel):
    id: int
    key: str
    name: str
    description: str | None = None


class RoleCreate(BaseModel):
    key: str
    name: str
    description: str | None = None
    is_system: bool = True


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class UserSummary(ORMBaseModel):
    id: int
    full_name: str
    email: EmailStr


class UserRead(ORMBaseModel):
    id: int
    employee_code: str | None = None
    full_name: str
    email: EmailStr
    mobile: str | None = None
    is_active: bool
    department: DepartmentBase | None = None
    roles: list[RoleRead] = []


class UserCreate(BaseModel):
    employee_code: str | None = None
    full_name: str
    email: EmailStr
    mobile: str | None = None
    password: str
    department_id: int | None = None
    role_ids: list[int]
    is_active: bool = True


class UserUpdate(BaseModel):
    employee_code: str | None = None
    full_name: str | None = None
    mobile: str | None = None
    department_id: int | None = None
    role_ids: list[int] | None = None
    is_active: bool | None = None
    password: str | None = None
