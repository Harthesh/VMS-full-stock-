from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import ORMBaseModel


class AppSettingRead(ORMBaseModel):
    id: int
    key: str
    value: str
    value_type: str
    description: str | None = None
    is_public: bool


class AppSettingUpdate(BaseModel):
    value: str
    value_type: str | None = None
    description: str | None = None
    is_public: bool | None = None

