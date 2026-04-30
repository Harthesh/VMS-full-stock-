from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, has_any_role
from app.core.enums import RoleKey
from app.db.session import get_db
from app.models.rbac import User
from app.schemas.common import MessageResponse
from app.schemas.invitation import (
    InvitationCreate,
    InvitationListItem,
    InvitationPublicSubmit,
    InvitationPublicView,
)
from app.schemas.visitor_request import VisitorRequestRead
from app.services.invitation_service import (
    cancel_invitation,
    create_invitation,
    get_by_token,
    get_invitation_or_404,
    list_invitations,
    send_invitation_email,
    submit_invitation,
)
from app.services.visitor_request_service import get_request_or_404

router = APIRouter()
public_router = APIRouter()


# --- Authenticated (host) endpoints ---
@router.post(
    "",
    response_model=InvitationListItem,
    status_code=status.HTTP_201_CREATED,
)
def create(
    payload: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvitationListItem:
    inv = create_invitation(db, payload, current_user)
    public_link = f"{settings.public_app_url.rstrip('/')}/invite/{inv.token}"
    send_invitation_email(db, inv, public_link=public_link)
    db.commit()
    db.refresh(inv)
    return inv


@router.get("", response_model=list[InvitationListItem])
def list_all(
    only_mine: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[InvitationListItem]:
    can_see_all = has_any_role(current_user, {RoleKey.ADMIN, RoleKey.HR})
    return list_invitations(db, current_user, only_mine=(only_mine or not can_see_all))


@router.get("/{invitation_id}", response_model=InvitationListItem)
def get_one(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvitationListItem:
    inv = get_invitation_or_404(db, invitation_id)
    if (
        inv.host_user_id != current_user.id
        and not has_any_role(current_user, {RoleKey.ADMIN, RoleKey.HR})
    ):
        raise HTTPException(status_code=403, detail="Forbidden")
    return inv


@router.delete("/{invitation_id}", response_model=MessageResponse)
def cancel(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    inv = get_invitation_or_404(db, invitation_id)
    cancel_invitation(db, inv, current_user)
    db.commit()
    return MessageResponse(message="Invitation cancelled")


@router.post("/{invitation_id}/resend", response_model=MessageResponse)
def resend(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    inv = get_invitation_or_404(db, invitation_id)
    if (
        inv.host_user_id != current_user.id
        and not has_any_role(current_user, {RoleKey.ADMIN, RoleKey.HR})
    ):
        raise HTTPException(status_code=403, detail="Forbidden")
    public_link = f"{settings.public_app_url.rstrip('/')}/invite/{inv.token}"
    send_invitation_email(db, inv, public_link=public_link)
    db.commit()
    return MessageResponse(message="Invitation email resent")


# --- Public (no-auth) endpoints ---
@public_router.get("/{token}", response_model=InvitationPublicView)
def public_view(token: str, db: Session = Depends(get_db)) -> InvitationPublicView:
    inv = get_by_token(db, token)
    db.commit()  # may have flipped to expired
    return InvitationPublicView(
        visitor_name=inv.visitor_name,
        visitor_email=inv.visitor_email,
        visitor_mobile=inv.visitor_mobile,
        company_name=inv.company_name,
        visitor_type=inv.visitor_type,
        visit_date=inv.visit_date,
        visit_time=inv.visit_time,
        purpose=inv.purpose,
        host_name=inv.host.full_name if inv.host else "—",
        host_email=inv.host.email if inv.host else "",
        expires_at=inv.expires_at,
        status=inv.status,
    )


@public_router.post(
    "/{token}/submit",
    response_model=VisitorRequestRead,
    status_code=status.HTTP_201_CREATED,
)
def public_submit(
    token: str,
    payload: InvitationPublicSubmit,
    db: Session = Depends(get_db),
) -> VisitorRequestRead:
    inv = get_by_token(db, token)
    visitor_request = submit_invitation(db, inv, payload)
    db.commit()
    return get_request_or_404(db, visitor_request.id)


