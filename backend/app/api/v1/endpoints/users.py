from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.core.enums import RoleKey
from app.db.session import get_db
from app.models.rbac import User
from app.schemas.user import DepartmentBase, RoleRead, UserCreate, UserRead, UserUpdate
from app.schemas.user import RoleCreate, RoleUpdate, UserSummary
from app.services.user_service import (
    create_role,
    create_user,
    list_departments,
    list_roles,
    list_user_directory,
    list_users,
    update_role,
    update_user,
)

router = APIRouter()


@router.get("", response_model=list[UserRead])
def get_users(
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN)),
) -> list[UserRead]:
    return list_users(db)


@router.post("", response_model=UserRead)
def create_user_endpoint(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN)),
) -> UserRead:
    return create_user(db, payload)


@router.patch("/{user_id}", response_model=UserRead)
def update_user_endpoint(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN)),
) -> UserRead:
    return update_user(db, user_id, payload)


@router.get("/directory", response_model=list[UserSummary])
def get_user_directory(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[UserSummary]:
    return list_user_directory(db)


@router.get("/roles", response_model=list[RoleRead])
def get_roles(
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN)),
) -> list[RoleRead]:
    return list_roles(db)


@router.post("/roles", response_model=RoleRead)
def create_role_endpoint(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN)),
) -> RoleRead:
    role = create_role(db, payload)
    db.commit()
    return role


@router.patch("/roles/{role_id}", response_model=RoleRead)
def update_role_endpoint(
    role_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN)),
) -> RoleRead:
    role = update_role(db, role_id, payload)
    db.commit()
    return role


@router.get("/departments", response_model=list[DepartmentBase])
def get_departments(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[DepartmentBase]:
    return list_departments(db)
