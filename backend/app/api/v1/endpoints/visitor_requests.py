from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.rbac import User
from app.schemas.common import MessageResponse
from app.schemas.visitor_request import VisitorDocumentRead, VisitorRequestCreate, VisitorRequestListItem, VisitorRequestRead, VisitorRequestUpdate
from app.services.document_service import upload_request_documents
from app.services.visitor_request_service import (
    cancel_request,
    create_request,
    ensure_request_access,
    get_request_or_404,
    list_requests,
    submit_existing_request,
    update_request,
)

router = APIRouter()


@router.get("", response_model=list[VisitorRequestListItem])
def get_visitor_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[VisitorRequestListItem]:
    return list_requests(db, current_user)


@router.post("", response_model=VisitorRequestRead)
def create_visitor_request(
    payload: VisitorRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VisitorRequestRead:
    request = create_request(db, payload, current_user)
    db.commit()
    return request


@router.get("/{request_id}", response_model=VisitorRequestRead)
def get_visitor_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VisitorRequestRead:
    request = get_request_or_404(db, request_id)
    ensure_request_access(request, current_user)
    return request


@router.patch("/{request_id}", response_model=VisitorRequestRead)
def update_visitor_request(
    request_id: int,
    payload: VisitorRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VisitorRequestRead:
    request = get_request_or_404(db, request_id)
    updated = update_request(db, request, payload, current_user)
    db.commit()
    return updated


@router.post("/{request_id}/submit", response_model=VisitorRequestRead)
def submit_visitor_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VisitorRequestRead:
    request = get_request_or_404(db, request_id)
    updated = submit_existing_request(db, request, current_user)
    db.commit()
    return updated


@router.post("/{request_id}/cancel", response_model=VisitorRequestRead)
def cancel_visitor_request(
    request_id: int,
    payload: MessageResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VisitorRequestRead:
    request = get_request_or_404(db, request_id)
    updated = cancel_request(db, request, current_user, payload.message)
    db.commit()
    return updated


@router.post("/{request_id}/documents", response_model=list[VisitorDocumentRead])
def upload_documents(
    request_id: int,
    document_type: str,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[VisitorDocumentRead]:
    request = get_request_or_404(db, request_id)
    documents = upload_request_documents(
        db,
        visitor_request=request,
        actor=current_user,
        files=files,
        document_type=document_type,
    )
    db.commit()
    return documents

