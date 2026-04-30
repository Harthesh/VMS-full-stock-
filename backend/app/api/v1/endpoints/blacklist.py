from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.core.enums import RoleKey
from app.db.session import get_db
from app.models.rbac import User
from app.schemas.blacklist import BlacklistCreate, BlacklistRead, BlacklistUpdate
from app.services.blacklist_service import create_blacklist_entry, list_blacklist, search_blacklist, update_blacklist_entry

router = APIRouter()


@router.get("", response_model=list[BlacklistRead])
def get_blacklist(
    visitor_name: str | None = Query(default=None),
    mobile: str | None = Query(default=None),
    id_proof_number: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.ADMIN, RoleKey.GATEKEEPER)),
) -> list[BlacklistRead]:
    if visitor_name or mobile or id_proof_number:
        return search_blacklist(db, visitor_name=visitor_name, mobile=mobile, id_proof_number=id_proof_number)
    return list_blacklist(db)


@router.post("", response_model=BlacklistRead)
def create_blacklist(
    payload: BlacklistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.ADMIN)),
) -> BlacklistRead:
    entry = create_blacklist_entry(db, payload, current_user.id)
    db.commit()
    return entry


@router.patch("/{entry_id}", response_model=BlacklistRead)
def update_blacklist(
    entry_id: int,
    payload: BlacklistUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles(RoleKey.SECURITY, RoleKey.ADMIN)),
) -> BlacklistRead:
    entry = update_blacklist_entry(db, entry_id, payload)
    db.commit()
    return entry

