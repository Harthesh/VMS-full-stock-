from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import RoleKey
from app.core.security import create_password_hash
from app.models.rbac import Department, Role, User, UserRole
from app.models.workflow import AppSetting


ROLE_SEEDS = [
    (RoleKey.EMPLOYEE.value, "Employee", "Create supplier and contractor requests"),
    (RoleKey.HR.value, "HR", "Create and manage candidate requests"),
    (RoleKey.BD_SALES.value, "BD / Sales", "Create and manage customer and VIP requests"),
    (RoleKey.MANAGER.value, "Manager", "Approves supplier and departmental requests"),
    (RoleKey.HOD.value, "HOD", "Approves customer and contractor requests"),
    (RoleKey.CEO_OFFICE.value, "CEO Office", "Final approval for VIP visits"),
    (RoleKey.SECURITY.value, "Security", "Security clearance and watchlist handling"),
    (RoleKey.IT.value, "IT", "Approves contractor IT access"),
    (RoleKey.GATEKEEPER.value, "Gatekeeper", "Performs check-in and check-out"),
    (RoleKey.ADMIN.value, "Admin", "Full system access"),
]

DEPARTMENT_SEEDS = [
    ("ADM", "Administration"),
    ("HR", "Human Resources"),
    ("SAL", "Sales"),
    ("OPS", "Operations"),
    ("SEC", "Security"),
    ("INF", "Information Technology"),
]

SETTING_SEEDS = [
    ("blacklist_default_action", "block", "string", "Default action when a blacklist rule does not override it"),
    ("badge_prefix", "BADGE", "string", "Prefix used for badge number generation"),
    ("email_notifications_enabled", "true", "boolean", "Toggle for future SMTP delivery"),
]


def seed_reference_data(db: Session) -> None:
    for key, name, description in ROLE_SEEDS:
        role = db.execute(select(Role).where(Role.key == key)).scalar_one_or_none()
        if not role:
            db.add(Role(key=key, name=name, description=description, is_system=True))

    for code, name in DEPARTMENT_SEEDS:
        department = db.execute(select(Department).where(Department.code == code)).scalar_one_or_none()
        if not department:
            db.add(Department(code=code, name=name))

    for key, value, value_type, description in SETTING_SEEDS:
        setting = db.execute(select(AppSetting).where(AppSetting.key == key)).scalar_one_or_none()
        if not setting:
            db.add(AppSetting(key=key, value=value, value_type=value_type, description=description))

    db.flush()


def seed_default_admin(db: Session) -> User:
    admin = db.execute(select(User).where(User.email == settings.default_admin_email)).scalar_one_or_none()
    if admin:
        return admin

    admin_department = db.execute(select(Department).where(Department.code == "ADM")).scalar_one()
    admin_role = db.execute(select(Role).where(Role.key == RoleKey.ADMIN.value)).scalar_one()
    admin = User(
        full_name="System Administrator",
        email=settings.default_admin_email,
        hashed_password=create_password_hash(settings.default_admin_password),
        department_id=admin_department.id,
        is_active=True,
    )
    db.add(admin)
    db.flush()
    db.add(UserRole(user_id=admin.id, role_id=admin_role.id))
    db.flush()
    return admin

