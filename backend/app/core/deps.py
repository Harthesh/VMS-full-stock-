from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import RoleKey
from app.core.security import decode_token
from app.db.session import get_db
from app.models.rbac import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise credentials_exception

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_exception
    return user


def has_any_role(user: User, role_keys: set[RoleKey | str]) -> bool:
    user_role_keys = {role.key for role in user.roles}
    return bool(user_role_keys.intersection({str(key) for key in role_keys}))


def require_roles(*role_keys: RoleKey) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if has_any_role(current_user, {RoleKey.ADMIN}) or has_any_role(current_user, set(role_keys)):
            return current_user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return dependency

