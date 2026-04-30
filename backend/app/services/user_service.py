from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import create_password_hash
from app.models.rbac import Department, Role, User, UserRole
from app.schemas.user import RoleCreate, RoleUpdate, UserCreate, UserUpdate


def list_users(db: Session) -> list[User]:
    statement = select(User).options(selectinload(User.roles), selectinload(User.department)).order_by(User.full_name.asc())
    return list(db.execute(statement).scalars().unique().all())


def list_user_directory(db: Session) -> list[User]:
    statement = select(User).where(User.is_active.is_(True)).order_by(User.full_name.asc())
    return list(db.execute(statement).scalars().all())


def create_user(db: Session, payload: UserCreate) -> User:
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    user = User(
        employee_code=payload.employee_code,
        full_name=payload.full_name,
        email=payload.email,
        mobile=payload.mobile,
        hashed_password=create_password_hash(payload.password),
        is_active=payload.is_active,
        department_id=payload.department_id,
    )
    db.add(user)
    db.flush()
    _replace_roles(db, user, payload.role_ids)
    db.flush()
    return get_user_or_404(db, user.id)


def get_user_or_404(db: Session, user_id: int) -> User:
    statement = select(User).options(selectinload(User.roles), selectinload(User.department)).where(User.id == user_id)
    user = db.execute(statement).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    values = payload.model_dump(exclude_unset=True, exclude={"role_ids", "password"})
    for key, value in values.items():
        setattr(user, key, value)
    if payload.password:
        user.hashed_password = create_password_hash(payload.password)
    if payload.role_ids is not None:
        _replace_roles(db, user, payload.role_ids)
    db.flush()
    return get_user_or_404(db, user.id)


def _replace_roles(db: Session, user: User, role_ids: list[int]) -> None:
    db.query(UserRole).filter(UserRole.user_id == user.id).delete()
    roles = db.execute(select(Role).where(Role.id.in_(role_ids))).scalars().all()
    if len(roles) != len(set(role_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more roles are invalid")
    for role in roles:
        db.add(UserRole(user_id=user.id, role_id=role.id))


def list_roles(db: Session) -> list[Role]:
    return list(db.execute(select(Role).order_by(Role.name.asc())).scalars().all())


def list_departments(db: Session) -> list[Department]:
    return list(db.execute(select(Department).order_by(Department.name.asc())).scalars().all())


def create_role(db: Session, payload: RoleCreate) -> Role:
    existing = db.execute(select(Role).where(Role.key == payload.key)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role key already exists")
    role = Role(**payload.model_dump())
    db.add(role)
    db.flush()
    return role


def update_role(db: Session, role_id: int, payload: RoleUpdate) -> Role:
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(role, key, value)
    db.flush()
    return role
