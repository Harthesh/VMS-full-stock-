from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.core.enums import RoleKey
from app.db.session import get_db
from app.models.workflow import AppSetting
from app.schemas.setting import AppSettingRead, AppSettingUpdate

router = APIRouter()


@router.get("", response_model=list[AppSettingRead])
def list_settings(
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN)),
) -> list[AppSettingRead]:
    return list(db.execute(select(AppSetting).order_by(AppSetting.key.asc())).scalars().all())


@router.put("/{key}", response_model=AppSettingRead)
def update_setting(
    key: str,
    payload: AppSettingUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN)),
) -> AppSettingRead:
    setting = db.execute(select(AppSetting).where(AppSetting.key == key)).scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(setting, field, value)
    db.commit()
    db.refresh(setting)
    return setting

