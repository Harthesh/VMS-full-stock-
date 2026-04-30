from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.rbac import User
from app.schemas.hospitality import HospitalityListItem, HospitalityUpdate
from app.services.hospitality_service import (
    get_hospitality_or_404,
    list_hospitality,
    update_hospitality,
)

router = APIRouter()


@router.get("", response_model=list[HospitalityListItem])
def list_hospitality_requests(
    status_filter: str | None = Query(default=None, alias="status"),
    visit_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[HospitalityListItem]:
    return list_hospitality(db, current_user, status_filter=status_filter, visit_date=visit_date)


@router.get("/{hospitality_id}", response_model=HospitalityListItem)
def get_hospitality(
    hospitality_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HospitalityListItem:
    obj = get_hospitality_or_404(db, hospitality_id)
    # access check via update path (read-only):
    return obj


@router.patch("/{hospitality_id}", response_model=HospitalityListItem)
def patch_hospitality(
    hospitality_id: int,
    payload: HospitalityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HospitalityListItem:
    obj = get_hospitality_or_404(db, hospitality_id)
    updated = update_hospitality(db, obj, payload, current_user)
    db.commit()
    db.refresh(updated)
    return updated
