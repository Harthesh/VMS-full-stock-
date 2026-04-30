from __future__ import annotations

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.rbac import User
from app.models.visitor import VisitorDocument, VisitorRequest
from app.services.audit_service import record_audit_log
from app.services.storage_service import storage_service
from app.services.visitor_request_service import ensure_request_access


def upload_request_documents(
    db: Session,
    *,
    visitor_request: VisitorRequest,
    actor: User,
    files: list[UploadFile],
    document_type: str,
) -> list[VisitorDocument]:
    ensure_request_access(visitor_request, actor)
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files received")

    documents: list[VisitorDocument] = []
    for upload in files:
        file_name, file_path = storage_service.save(upload, f"visitor_requests/{visitor_request.id}/documents")
        document = VisitorDocument(
            visitor_request_id=visitor_request.id,
            document_type=document_type,
            file_name=file_name,
            file_path=file_path,
            content_type=upload.content_type,
            uploaded_by_user_id=actor.id,
        )
        db.add(document)
        documents.append(document)

    record_audit_log(
        db,
        entity_type="visitor_request",
        entity_id=visitor_request.id,
        action="documents_uploaded",
        actor_user_id=actor.id,
        details={"document_type": document_type, "count": len(documents)},
    )
    db.flush()
    return documents

