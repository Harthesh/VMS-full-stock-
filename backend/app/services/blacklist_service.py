from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.workflow import VisitorBlacklist
from app.schemas.blacklist import BlacklistCreate, BlacklistUpdate


def list_blacklist(db: Session) -> list[VisitorBlacklist]:
    statement = select(VisitorBlacklist).options(selectinload(VisitorBlacklist.added_by)).order_by(VisitorBlacklist.id.desc())
    return list(db.execute(statement).scalars().all())


def create_blacklist_entry(db: Session, payload: BlacklistCreate, actor_user_id: int | None) -> VisitorBlacklist:
    entry = VisitorBlacklist(**payload.model_dump(), added_by_user_id=actor_user_id)
    db.add(entry)
    db.flush()
    return entry


def update_blacklist_entry(db: Session, entry_id: int, payload: BlacklistUpdate) -> VisitorBlacklist:
    entry = db.get(VisitorBlacklist, entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blacklist entry not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    db.flush()
    return entry


def search_blacklist(
    db: Session,
    *,
    visitor_name: str | None = None,
    mobile: str | None = None,
    id_proof_number: str | None = None,
) -> list[VisitorBlacklist]:
    filters = [VisitorBlacklist.is_active.is_(True)]
    matchers = []
    if visitor_name:
        matchers.append(VisitorBlacklist.visitor_name.ilike(f"%{visitor_name}%"))
    if mobile:
        matchers.append(VisitorBlacklist.mobile == mobile)
    if id_proof_number:
        matchers.append(VisitorBlacklist.id_proof_number == id_proof_number)
    statement = select(VisitorBlacklist).options(selectinload(VisitorBlacklist.added_by)).where(*filters)
    if matchers:
        statement = statement.where(or_(*matchers))
    return list(db.execute(statement).scalars().all())


def find_blacklist_match(
    db: Session,
    *,
    visitor_name: str,
    mobile: str | None,
    id_proof_number: str | None,
) -> VisitorBlacklist | None:
    matches = search_blacklist(
        db, visitor_name=visitor_name, mobile=mobile, id_proof_number=id_proof_number
    )
    return matches[0] if matches else None

