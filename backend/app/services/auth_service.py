from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import create_access_token, verify_password
from app.models.rbac import User
from app.schemas.auth import CurrentUserResponse, TokenResponse
from app.schemas.user import RoleRead


def authenticate_user(db: Session, email: str, password: str) -> User:
    statement = select(User).options(selectinload(User.roles)).where(User.email == email)
    user = db.execute(statement).scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
    return user


def build_current_user_response(user: User) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        department_id=user.department_id,
        roles=[RoleRead.model_validate(role) for role in user.roles],
    )


def login(db: Session, email: str, password: str) -> TokenResponse:
    user = authenticate_user(db, email, password)
    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token, user=build_current_user_response(user))

