from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.core.enums import RoleKey
from app.db.session import get_db
from app.schemas.report import (
    BlacklistAlertRow,
    DailyGateMovementRow,
    PendingApprovalRow,
    VisitorSummaryRow,
    VisitorTypeSummaryRow,
)
from app.services.report_service import (
    get_blacklist_alert_report,
    get_daily_gate_movement,
    get_pending_approval_report,
    get_visitor_summary,
    get_visitor_type_summary,
)

router = APIRouter()


@router.get("/visitor-summary", response_model=list[VisitorSummaryRow])
def visitor_summary(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN, RoleKey.SECURITY, RoleKey.HR, RoleKey.BD_SALES, RoleKey.MANAGER, RoleKey.HOD)),
) -> list[VisitorSummaryRow]:
    return get_visitor_summary(db, start_date, end_date)


@router.get("/daily-gate-movement", response_model=list[DailyGateMovementRow])
def daily_gate_movement(
    report_date: date | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN, RoleKey.SECURITY, RoleKey.GATEKEEPER)),
) -> list[DailyGateMovementRow]:
    return get_daily_gate_movement(db, report_date, start_date, end_date)


@router.get("/pending-approvals", response_model=list[PendingApprovalRow])
def pending_approvals_report(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN, RoleKey.MANAGER, RoleKey.HOD, RoleKey.CEO_OFFICE, RoleKey.SECURITY, RoleKey.IT)),
) -> list[PendingApprovalRow]:
    return get_pending_approval_report(db, start_date, end_date)


@router.get("/blacklist-alerts", response_model=list[BlacklistAlertRow])
def blacklist_alert_report(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN, RoleKey.SECURITY, RoleKey.GATEKEEPER)),
) -> list[BlacklistAlertRow]:
    return get_blacklist_alert_report(db, start_date, end_date)


@router.get("/visitor-type-summary", response_model=list[VisitorTypeSummaryRow])
def visitor_type_summary(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleKey.ADMIN, RoleKey.SECURITY, RoleKey.HR, RoleKey.BD_SALES, RoleKey.MANAGER, RoleKey.HOD)),
) -> list[VisitorTypeSummaryRow]:
    return get_visitor_type_summary(db, start_date, end_date)
