from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.rbac import User
from app.schemas.approval import ApprovalActionCreate
from app.schemas.visitor_request import VisitorRequestRead
from app.services.visitor_request_service import get_request_or_404
from app.services.workflow_service import apply_approval_action, get_pending_approvals_for_user

router = APIRouter()


@router.get("/pending", response_model=list[VisitorRequestRead])
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[VisitorRequestRead]:
    return get_pending_approvals_for_user(db, current_user)


@router.post("/{request_id}/actions", response_model=VisitorRequestRead)
def act_on_approval(
    request_id: int,
    payload: ApprovalActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VisitorRequestRead:
    request = get_request_or_404(db, request_id)
    updated = apply_approval_action(
        db,
        request,
        action_type=payload.action,
        remarks=payload.remarks,
        actor=current_user,
    )
    db.commit()
    return updated

