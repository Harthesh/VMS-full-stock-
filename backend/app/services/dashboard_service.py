from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import ApprovalStepStatus, GateAction, VisitorRequestStatus
from app.models.visitor import VisitorLog, VisitorRequest
from app.models.workflow import ApprovalStep
from app.schemas.dashboard import DashboardSummary


def get_dashboard_summary(db: Session) -> DashboardSummary:
    today = date.today()
    date_window = [today - timedelta(days=offset) for offset in range(6, -1, -1)]

    total_requests_today = db.execute(
        select(func.count()).select_from(VisitorRequest).where(VisitorRequest.request_date == today)
    ).scalar_one()
    pending_approvals = db.execute(
        select(func.count()).select_from(ApprovalStep).where(ApprovalStep.status == ApprovalStepStatus.ACTIVE)
    ).scalar_one()
    approved_visitors_today = db.execute(
        select(func.count()).select_from(VisitorRequest).where(
            VisitorRequest.visit_date == today,
            VisitorRequest.status.in_([VisitorRequestStatus.APPROVED, VisitorRequestStatus.CHECKED_IN, VisitorRequestStatus.CHECKED_OUT]),
        )
    ).scalar_one()
    checked_in_visitors_now = db.execute(
        select(func.count()).select_from(VisitorRequest).where(VisitorRequest.status == VisitorRequestStatus.CHECKED_IN)
    ).scalar_one()
    checked_out_visitors_today = db.execute(
        select(func.count()).select_from(VisitorRequest).where(
            VisitorRequest.check_out_time.is_not(None),
            func.date(VisitorRequest.check_out_time) == today,
        )
    ).scalar_one()
    blacklisted_visitors_detected = db.execute(
        select(func.count()).select_from(VisitorLog).where(VisitorLog.action == GateAction.ACCESS_BLOCKED)
    ).scalar_one()

    visitor_count_by_type_rows = db.execute(
        select(VisitorRequest.visitor_type, func.count()).group_by(VisitorRequest.visitor_type)
    ).all()
    approval_pending_by_role_rows = db.execute(
        select(ApprovalStep.role_key, func.count()).where(ApprovalStep.status == ApprovalStepStatus.ACTIVE).group_by(ApprovalStep.role_key)
    ).all()

    trend_chart: list[dict[str, int | str]] = []
    for chart_date in date_window:
        count = db.execute(
            select(func.count()).select_from(VisitorRequest).where(VisitorRequest.request_date == chart_date)
        ).scalar_one()
        trend_chart.append({"date": chart_date.isoformat(), "count": count})

    return DashboardSummary(
        total_requests_today=total_requests_today,
        pending_approvals=pending_approvals,
        approved_visitors_today=approved_visitors_today,
        checked_in_visitors_now=checked_in_visitors_now,
        checked_out_visitors_today=checked_out_visitors_today,
        blacklisted_visitors_detected=blacklisted_visitors_detected,
        visitor_count_by_type={row[0].value: row[1] for row in visitor_count_by_type_rows},
        approval_pending_by_role={row[0]: row[1] for row in approval_pending_by_role_rows},
        trend_chart=trend_chart,
    )

