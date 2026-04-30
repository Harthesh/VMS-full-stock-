from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import RoleKey, VisitorRequestStatus
from app.db.session import SessionLocal
from app.models.rbac import Role, User, UserRole
from app.models.visitor import HospitalityRequest, VisitorRequest
from app.services.email_service import send_bulk_email

logger = logging.getLogger(__name__)


def _emails_for_roles(db: Session, role_keys: list[str]) -> list[str]:
    rows = (
        db.execute(
            select(User.email)
            .join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .where(Role.key.in_(role_keys), User.is_active.is_(True))
        )
        .scalars()
        .all()
    )
    return [r for r in rows if r]


def _with_session(fn):
    """Decorator: open a Session, run, commit, close — used by APScheduler jobs."""

    def wrapper(*args, **kwargs):
        db: Session = SessionLocal()
        try:
            fn(db, *args, **kwargs)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Scheduled job %s failed", fn.__name__)
            raise
        finally:
            db.close()

    wrapper.__name__ = fn.__name__
    return wrapper


# ---------- Daily Hospitality Digest (7 AM) ---------- #
@_with_session
def run_daily_hospitality_digest(db: Session) -> None:
    today = date.today()
    rows = (
        db.execute(
            select(VisitorRequest)
            .options(selectinload(VisitorRequest.host_user), selectinload(VisitorRequest.hospitality_request))
            .where(
                VisitorRequest.visit_date == today,
                VisitorRequest.requires_hospitality.is_(True),
                VisitorRequest.status.in_(
                    [
                        VisitorRequestStatus.APPROVED,
                        VisitorRequestStatus.SCHEDULED,
                        VisitorRequestStatus.PENDING_LOGISTICS_CONFIRMATION,
                    ]
                ),
            )
            .order_by(VisitorRequest.visit_time.asc().nullslast())
        )
        .scalars()
        .all()
    )

    recipients = _emails_for_roles(db, [RoleKey.ADMIN.value, RoleKey.HR.value])
    if not recipients:
        logger.info("Daily digest: no recipients configured (admin/hr roles empty)")
        return

    if not rows:
        text = f"No hospitality-tagged visits scheduled for {today.isoformat()}."
        html = f"<p>No hospitality-tagged visits scheduled for <strong>{today.isoformat()}</strong>.</p>"
    else:
        lines = [f"Hospitality schedule for {today.isoformat()} ({len(rows)} visits):", ""]
        html_rows = []
        for vr in rows:
            t = vr.visit_time.strftime("%H:%M") if vr.visit_time else "TBD"
            host = vr.host_user.full_name if vr.host_user else "-"
            hr = vr.hospitality_request
            tags = []
            if hr:
                if hr.meal_required:
                    tags.append("meal")
                if hr.transport_required:
                    tags.append("transport")
                if hr.escort_needed:
                    tags.append("escort")
                if hr.meeting_room:
                    tags.append(f"room:{hr.meeting_room}")
            tag_str = ", ".join(tags) if tags else "general"
            lines.append(f"  {t}  {vr.request_no}  {vr.visitor_name} (host: {host}) — {tag_str}")
            html_rows.append(
                f"<tr><td>{t}</td><td>{vr.request_no}</td><td>{vr.visitor_name}</td>"
                f"<td>{host}</td><td>{tag_str}</td></tr>"
            )
        text = "\n".join(lines)
        html = (
            f"<h3>Hospitality schedule for {today.isoformat()}</h3>"
            "<table border='1' cellpadding='6' cellspacing='0'>"
            "<tr><th>Time</th><th>Request</th><th>Visitor</th><th>Host</th><th>Services</th></tr>"
            + "".join(html_rows)
            + "</table>"
        )

    send_bulk_email(
        db,
        event_type="daily_hospitality_digest",
        recipients=recipients,
        subject=f"Daily Hospitality Digest — {today.isoformat()}",
        text_body=text,
        html_body=html,
        payload={"date": today.isoformat(), "visits": len(rows)},
    )


# ---------- Unchecked-Out Alert (8 PM) ---------- #
@_with_session
def run_unchecked_out_alerts(db: Session) -> None:
    today = date.today()
    rows = (
        db.execute(
            select(VisitorRequest)
            .options(selectinload(VisitorRequest.host_user))
            .where(
                VisitorRequest.status == VisitorRequestStatus.CHECKED_IN,
                VisitorRequest.check_in_time.is_not(None),
                VisitorRequest.check_out_time.is_(None),
            )
            .order_by(VisitorRequest.check_in_time.asc())
        )
        .scalars()
        .all()
    )
    if not rows:
        logger.info("Unchecked-out: no pending visitors at end of day")
        return

    recipients = _emails_for_roles(db, [RoleKey.SECURITY.value, RoleKey.GATEKEEPER.value, RoleKey.ADMIN.value])
    if not recipients:
        logger.info("Unchecked-out: no security recipients configured")
        return

    lines = [f"Visitors still checked-in as of {today.isoformat()} EOD ({len(rows)}):", ""]
    html_rows = []
    for vr in rows:
        ci = vr.check_in_time.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M") if vr.check_in_time else "-"
        host = vr.host_user.full_name if vr.host_user else "-"
        lines.append(f"  {vr.request_no}  {vr.visitor_name}  in:{ci}  host:{host}")
        html_rows.append(
            f"<tr><td>{vr.request_no}</td><td>{vr.visitor_name}</td><td>{ci}</td><td>{host}</td></tr>"
        )
    text = "\n".join(lines)
    html = (
        f"<h3>Visitors not yet checked out — {today.isoformat()}</h3>"
        "<table border='1' cellpadding='6' cellspacing='0'>"
        "<tr><th>Request</th><th>Visitor</th><th>Check-in (UTC)</th><th>Host</th></tr>"
        + "".join(html_rows)
        + "</table>"
        "<p>Please reconcile gate logs and physical presence.</p>"
    )

    send_bulk_email(
        db,
        event_type="unchecked_out_alert",
        recipients=recipients,
        subject=f"Unchecked-Out Visitors Alert — {today.isoformat()}",
        text_body=text,
        html_body=html,
        payload={"date": today.isoformat(), "open_visits": len(rows)},
    )


# ---------- No-Show Alert (9 PM) ---------- #
@_with_session
def run_no_show_alerts(db: Session) -> None:
    today = date.today()
    rows = (
        db.execute(
            select(VisitorRequest)
            .options(selectinload(VisitorRequest.host_user))
            .where(
                VisitorRequest.visit_date == today,
                VisitorRequest.status.in_([VisitorRequestStatus.APPROVED, VisitorRequestStatus.SCHEDULED]),
                VisitorRequest.check_in_time.is_(None),
            )
        )
        .scalars()
        .all()
    )
    if not rows:
        logger.info("No-show: no candidates today")
        return

    # Group by host so each host gets one email about their no-shows.
    by_host: dict[int, list[VisitorRequest]] = {}
    fallback: list[VisitorRequest] = []
    for vr in rows:
        if vr.host_user and vr.host_user.email and vr.host_user.is_active:
            by_host.setdefault(vr.host_user.id, []).append(vr)
        else:
            fallback.append(vr)

    for host_id, items in by_host.items():
        host = items[0].host_user
        lines = [f"Hello {host.full_name},", "", f"The following approved visitors did not check in today ({today.isoformat()}):", ""]
        for vr in items:
            t = vr.visit_time.strftime("%H:%M") if vr.visit_time else "TBD"
            lines.append(f"  {vr.request_no}  {vr.visitor_name}  scheduled:{t}")
        lines += ["", "Please reach out to confirm or reschedule."]
        text = "\n".join(lines)
        send_bulk_email(
            db,
            event_type="no_show_alert",
            recipients=[host.email],
            subject=f"No-Show Alert — {len(items)} visitor(s) on {today.isoformat()}",
            text_body=text,
            html_body=text.replace("\n", "<br/>"),
            payload={"host_id": host_id, "count": len(items), "request_ids": [vr.id for vr in items]},
        )

    if fallback:
        admins = _emails_for_roles(db, [RoleKey.ADMIN.value])
        if admins:
            text = "\n".join(
                [f"No-show visitors with no host email ({today.isoformat()}):", ""]
                + [f"  {vr.request_no}  {vr.visitor_name}" for vr in fallback]
            )
            send_bulk_email(
                db,
                event_type="no_show_alert_fallback",
                recipients=admins,
                subject=f"No-Show Alert (no host) — {today.isoformat()}",
                text_body=text,
                payload={"count": len(fallback), "request_ids": [vr.id for vr in fallback]},
            )


# ---------- Manual trigger helper for API/testing ---------- #
def run_job_by_id(job_id: str) -> None:
    fn_map = {
        "daily_hospitality_digest": run_daily_hospitality_digest,
        "unchecked_out_alerts": run_unchecked_out_alerts,
        "no_show_alerts": run_no_show_alerts,
    }
    fn = fn_map.get(job_id)
    if fn is None:
        raise ValueError(f"Unknown job_id: {job_id}")
    fn()
