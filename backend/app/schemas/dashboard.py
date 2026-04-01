from __future__ import annotations

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_requests_today: int
    pending_approvals: int
    approved_visitors_today: int
    checked_in_visitors_now: int
    checked_out_visitors_today: int
    blacklisted_visitors_detected: int
    visitor_count_by_type: dict[str, int]
    approval_pending_by_role: dict[str, int]
    trend_chart: list[dict[str, int | str]]

