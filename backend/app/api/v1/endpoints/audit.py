from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.core.enums import RoleKey
from app.db.session import get_db
from app.models.workflow import AuditLog
from app.schemas.audit import AuditLogRead

router = APIRouter()


@router.get("", response_model=list[AuditLogRead])
def get_audit_logs(
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN)),
) -> list[AuditLogRead]:
    return list(db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)).scalars().all())

