from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import ApprovalStepStatus, GateAction
from app.models.visitor import VisitorLog, VisitorRequest
from app.models.workflow import ApprovalStep
from app.schemas.report import (
    BlacklistAlertRow,
    DailyGateMovementRow,
    PendingApprovalRow,
    VisitorSummaryRow,
    VisitorTypeSummaryRow,
)


def get_visitor_summary(db: Session, start_date: date | None = None, end_date: date | None = None) -> list[VisitorSummaryRow]:
    statement = select(VisitorRequest).options(selectinload(VisitorRequest.host_user)).order_by(VisitorRequest.visit_date.desc())
    if start_date:
        statement = statement.where(VisitorRequest.visit_date >= start_date)
    if end_date:
        statement = statement.where(VisitorRequest.visit_date <= end_date)
    rows = db.execute(statement).scalars().all()
    return [
        VisitorSummaryRow(
            request_no=row.request_no,
            visitor_name=row.visitor_name,
            visitor_type=row.visitor_type.value,
            visit_date=row.visit_date,
            status=row.status.value,
            host_name=row.host_user.full_name if row.host_user else None,
        )
        for row in rows
    ]


def get_daily_gate_movement(
    db: Session, report_date: date | None = None, start_date: date | None = None, end_date: date | None = None
) -> list[DailyGateMovementRow]:
    statement = select(VisitorRequest).order_by(VisitorRequest.check_in_time.asc())
    if report_date:
        statement = statement.where(VisitorRequest.visit_date == report_date)
    if start_date:
        statement = statement.where(VisitorRequest.visit_date >= start_date)
    if end_date:
        statement = statement.where(VisitorRequest.visit_date <= end_date)
    if not any([report_date, start_date, end_date]):
        statement = statement.where(VisitorRequest.visit_date == date.today())
    rows = db.execute(statement).scalars().all()
    return [
        DailyGateMovementRow(
            request_no=row.request_no,
            visitor_name=row.visitor_name,
            check_in_time=row.check_in_time,
            check_out_time=row.check_out_time,
            badge_no=row.badge_no,
        )
        for row in rows
    ]


def get_pending_approval_report(db: Session, start_date: date | None = None, end_date: date | None = None) -> list[PendingApprovalRow]:
    statement = (
        select(VisitorRequest, ApprovalStep)
        .join(ApprovalStep, ApprovalStep.visitor_request_id == VisitorRequest.id)
        .where(ApprovalStep.status == ApprovalStepStatus.ACTIVE)
        .order_by(VisitorRequest.visit_date.asc())
    )
    if start_date:
        statement = statement.where(VisitorRequest.visit_date >= start_date)
    if end_date:
        statement = statement.where(VisitorRequest.visit_date <= end_date)
    rows = (
        db.execute(statement)
        .all()
    )
    return [
        PendingApprovalRow(
            request_no=request.request_no,
            visitor_name=request.visitor_name,
            current_status=request.status.value,
            pending_role=step.role_key,
            visit_date=request.visit_date,
        )
        for request, step in rows
    ]


def get_blacklist_alert_report(db: Session, start_date: date | None = None, end_date: date | None = None) -> list[BlacklistAlertRow]:
    statement = (
        select(VisitorLog)
        .options(selectinload(VisitorLog.visitor_request))
        .where(VisitorLog.action.in_([GateAction.ACCESS_BLOCKED, GateAction.ACCESS_WARNING]))
    )
    if start_date:
        statement = statement.where(func.date(VisitorLog.created_at) >= start_date)
    if end_date:
        statement = statement.where(func.date(VisitorLog.created_at) <= end_date)
    rows = (
        db.execute(statement)
        .scalars()
        .all()
    )
    return [
        BlacklistAlertRow(
            request_no=row.visitor_request.request_no,
            visitor_name=row.visitor_request.visitor_name,
            action=row.action.value,
            remarks=row.remarks,
            created_at=row.created_at,
        )
        for row in rows
    ]


def get_visitor_type_summary(db: Session, start_date: date | None = None, end_date: date | None = None) -> list[VisitorTypeSummaryRow]:
    statement = select(VisitorRequest.visitor_type, func.count()).group_by(VisitorRequest.visitor_type)
    if start_date:
        statement = statement.where(VisitorRequest.visit_date >= start_date)
    if end_date:
        statement = statement.where(VisitorRequest.visit_date <= end_date)
    rows = db.execute(statement).all()
    return [VisitorTypeSummaryRow(visitor_type=visitor_type.value, count=count) for visitor_type, count in rows]
