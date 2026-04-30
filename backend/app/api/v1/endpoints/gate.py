from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.core.enums import RoleKey
from app.db.session import get_db
from app.models.rbac import User
from app.schemas.gate import GateActionPayload, GateActionResponse, GateLookupRequest, GateLookupResponse
from app.services.gate_service import check_in, check_out, lookup_request
from app.services.visitor_request_service import get_request_or_404

router = APIRouter()


@router.post("/lookup", response_model=GateLookupResponse)
def lookup_visitor(
    payload: GateLookupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleKey.GATEKEEPER, RoleKey.SECURITY, RoleKey.ADMIN)),
) -> GateLookupResponse:
    request, blacklist_action, blacklist_reason = lookup_request(db, **payload.model_dump())
    can_check_in = request.status.value in {"approved", "scheduled"} and blacklist_action != "block"
    can_check_out = request.status.value == "checked_in"
    return GateLookupResponse(
        request=request,
        badge=request.badge,
        host=request.host_user,
        blacklist_action=blacklist_action,
        blacklist_reason=blacklist_reason,
        can_check_in=can_check_in,
        can_check_out=can_check_out,
    )


@router.post("/{request_id}/check-in", response_model=GateActionResponse)
def check_in_visitor(
    request_id: int,
    payload: GateActionPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleKey.GATEKEEPER, RoleKey.SECURITY, RoleKey.ADMIN)),
) -> GateActionResponse:
    request = get_request_or_404(db, request_id)
    updated = check_in(db, request, current_user, gate_entry_point=payload.gate_entry_point, remarks=payload.remarks)
    db.commit()
    return GateActionResponse(
        request_id=updated.id,
        status=updated.status.value,
        check_in_time=updated.check_in_time,
        check_out_time=updated.check_out_time,
        remarks=payload.remarks,
    )


@router.post("/{request_id}/check-out", response_model=GateActionResponse)
def check_out_visitor(
    request_id: int,
    payload: GateActionPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleKey.GATEKEEPER, RoleKey.SECURITY, RoleKey.ADMIN)),
) -> GateActionResponse:
    request = get_request_or_404(db, request_id)
    updated = check_out(db, request, current_user, gate_entry_point=payload.gate_entry_point, remarks=payload.remarks)
    db.commit()
    return GateActionResponse(
        request_id=updated.id,
        status=updated.status.value,
        check_in_time=updated.check_in_time,
        check_out_time=updated.check_out_time,
        remarks=payload.remarks,
    )
