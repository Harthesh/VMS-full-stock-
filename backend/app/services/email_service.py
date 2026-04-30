from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr
from io import BytesIO

import qrcode
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import NotificationChannel, NotificationStatus
from app.models.visitor import VisitorRequest
from app.models.workflow import Notification


logger = logging.getLogger(__name__)


def _build_qr_png(qr_code_value: str) -> bytes:
    buffer = BytesIO()
    image = qrcode.make(qr_code_value)
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _build_approval_email(visitor_request: VisitorRequest, qr_png: bytes, recipient_email: str) -> EmailMessage:
    host_name = visitor_request.host_user.full_name if visitor_request.host_user else "Assigned host"
    visit_time = visitor_request.visit_time.strftime("%H:%M") if visitor_request.visit_time else "As scheduled"
    message = EmailMessage()
    message["Subject"] = f"Visitor Approval Confirmed - {visitor_request.request_no}"
    message["From"] = formataddr((settings.app_name, settings.default_from_email))
    message["To"] = recipient_email
    message.set_content(
        "\n".join(
            [
                f"Hello {visitor_request.visitor_name},",
                "",
                "Your visit request has been approved.",
                f"Request Number: {visitor_request.request_no}",
                f"Visit Date: {visitor_request.visit_date.isoformat()}",
                f"Visit Time: {visit_time}",
                f"Host: {host_name}",
                f"Visitor Email On Request: {visitor_request.email or '-'}",
                f"Badge Number: {visitor_request.badge.badge_no if visitor_request.badge else visitor_request.badge_no or '-'}",
                "",
                "Your QR code is attached to this email. Please present it at the gate.",
                f"QR Value: {visitor_request.badge.qr_code_value if visitor_request.badge else visitor_request.qr_code_value or '-'}",
            ]
        )
    )
    message.add_alternative(
        f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #1c1917;">
            <p>Hello {visitor_request.visitor_name},</p>
            <p>Your visit request has been approved. Please carry the attached QR code and present it at the gate.</p>
            <table style="border-collapse: collapse;">
              <tr><td style="padding: 4px 12px 4px 0;"><strong>Request Number</strong></td><td>{visitor_request.request_no}</td></tr>
              <tr><td style="padding: 4px 12px 4px 0;"><strong>Visit Date</strong></td><td>{visitor_request.visit_date.isoformat()}</td></tr>
              <tr><td style="padding: 4px 12px 4px 0;"><strong>Visit Time</strong></td><td>{visit_time}</td></tr>
              <tr><td style="padding: 4px 12px 4px 0;"><strong>Host</strong></td><td>{host_name}</td></tr>
              <tr><td style="padding: 4px 12px 4px 0;"><strong>Visitor Email On Request</strong></td><td>{visitor_request.email or "-"}</td></tr>
              <tr><td style="padding: 4px 12px 4px 0;"><strong>Badge Number</strong></td><td>{visitor_request.badge.badge_no if visitor_request.badge else visitor_request.badge_no or "-"}</td></tr>
            </table>
            <p style="margin-top: 16px;">QR Value: {visitor_request.badge.qr_code_value if visitor_request.badge else visitor_request.qr_code_value or "-"}</p>
          </body>
        </html>
        """,
        subtype="html",
    )
    message.add_attachment(
        qr_png,
        maintype="image",
        subtype="png",
        filename=f"{visitor_request.request_no}-qr.png",
    )
    return message


def _send_message(message: EmailMessage) -> None:
    if not settings.smtp_host:
        raise RuntimeError("SMTP host is not configured")

    if settings.smtp_use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            settings.smtp_host,
            settings.smtp_port,
            timeout=settings.smtp_timeout_seconds,
            context=context,
        ) as smtp:
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password or "")
            smtp.send_message(message)
        return

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout_seconds) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls(context=ssl.create_default_context())
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password or "")
        smtp.send_message(message)


def _send_simple_email(
    *,
    to: list[str],
    subject: str,
    text_body: str,
    html_body: str | None = None,
) -> None:
    if not to:
        return
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((settings.app_name, settings.default_from_email))
    message["To"] = ", ".join(to)
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype="html")
    _send_message(message)


def send_bulk_email(
    db: Session,
    *,
    event_type: str,
    recipients: list[str],
    subject: str,
    text_body: str,
    html_body: str | None = None,
    payload: dict | None = None,
) -> None:
    """Send an email to a list of recipients and record a Notification row.

    Used by scheduled jobs and ad-hoc alerts (gate, VIP, host, food dept, etc.).
    """
    recipients = [r for r in recipients if r]
    notification = Notification(
        recipient_user_id=None,
        channel=NotificationChannel.EMAIL,
        event_type=event_type,
        title=subject[:160],
        message=(text_body[:1000] if text_body else subject),
        status=NotificationStatus.PENDING,
        payload_json={
            "recipients": recipients,
            **(payload or {}),
        },
    )
    db.add(notification)
    db.flush()

    if not recipients or not settings.smtp_host:
        notification.status = NotificationStatus.FAILED
        notification.payload_json = {
            **(notification.payload_json or {}),
            "error": "no_recipients" if not recipients else "smtp_not_configured",
        }
        db.add(notification)
        db.flush()
        return

    try:
        _send_simple_email(to=recipients, subject=subject, text_body=text_body, html_body=html_body)
        notification.status = NotificationStatus.SENT
    except Exception as exc:
        notification.status = NotificationStatus.FAILED
        notification.payload_json = {
            **(notification.payload_json or {}),
            "error": str(exc),
        }
        logger.exception("Failed to send %s email", event_type)
    finally:
        db.add(notification)
        db.flush()


def send_visitor_rejection_email(db: Session, visitor_request: VisitorRequest, reason: str | None = None) -> None:
    recipient_email = settings.visitor_approval_test_email or visitor_request.email
    if not recipient_email:
        return
    subject = f"Visit Request Update — {visitor_request.request_no}"
    text = "\n".join(
        [
            f"Hello {visitor_request.visitor_name},",
            "",
            "Unfortunately your visit request has been rejected.",
            f"Request Number: {visitor_request.request_no}",
            f"Visit Date: {visitor_request.visit_date.isoformat()}",
            f"Reason: {reason or '-'}",
            "",
            "Please contact your host for more information.",
        ]
    )
    html = (
        f"<p>Hello {visitor_request.visitor_name},</p>"
        "<p>Unfortunately your visit request has been <strong>rejected</strong>.</p>"
        f"<table border='1' cellpadding='6' cellspacing='0'>"
        f"<tr><th align='left'>Request Number</th><td>{visitor_request.request_no}</td></tr>"
        f"<tr><th align='left'>Visit Date</th><td>{visitor_request.visit_date.isoformat()}</td></tr>"
        f"<tr><th align='left'>Reason</th><td>{reason or '-'}</td></tr>"
        "</table>"
        "<p>Please contact your host for more information.</p>"
    )
    send_bulk_email(
        db,
        event_type="visitor_rejection_email",
        recipients=[recipient_email],
        subject=subject,
        text_body=text,
        html_body=html,
        payload={"request_id": visitor_request.id, "reason": reason},
    )


def send_host_arrival_email(db: Session, visitor_request: VisitorRequest) -> None:
    if not visitor_request.host_user or not visitor_request.host_user.email:
        return
    recipient = visitor_request.host_user.email
    subject = f"Your visitor {visitor_request.visitor_name} has arrived"
    text = "\n".join(
        [
            f"Hello {visitor_request.host_user.full_name},",
            "",
            f"{visitor_request.visitor_name} ({visitor_request.company_name or 'no company'}) just checked in.",
            f"Request: {visitor_request.request_no}",
            f"Badge: {visitor_request.badge.badge_no if visitor_request.badge else '-'}",
            "",
            "Please proceed to receive them.",
        ]
    )
    send_bulk_email(
        db,
        event_type="host_arrival_email",
        recipients=[recipient],
        subject=subject,
        text_body=text,
        html_body=text.replace("\n", "<br/>"),
        payload={"request_id": visitor_request.id},
    )


def send_vip_alert_email(db: Session, visitor_request: VisitorRequest) -> None:
    from app.core.enums import RoleKey
    from app.models.rbac import Role, User as UserModel, UserRole

    rows = (
        db.execute(
            select(UserModel.email)
            .join(UserRole, UserRole.user_id == UserModel.id)
            .join(Role, Role.id == UserRole.role_id)
            .where(
                Role.key.in_([RoleKey.HOD.value, RoleKey.CEO_OFFICE.value, RoleKey.ADMIN.value]),
                UserModel.is_active.is_(True),
            )
        )
        .scalars()
        .all()
    )
    recipients = [r for r in rows if r]
    if not recipients:
        return
    subject = f"[VIP] Approval needed — {visitor_request.visitor_name}"
    text = "\n".join(
        [
            "A VIP visitor request requires escalated approval.",
            f"Request: {visitor_request.request_no}",
            f"Visitor: {visitor_request.visitor_name} ({visitor_request.company_name or '-'})",
            f"Visit Date: {visitor_request.visit_date.isoformat()}",
            f"Purpose: {visitor_request.purpose}",
            "",
            "Open the approvals queue to act.",
        ]
    )
    send_bulk_email(
        db,
        event_type="vip_alert_email",
        recipients=recipients,
        subject=subject,
        text_body=text,
        html_body=text.replace("\n", "<br/>"),
        payload={"request_id": visitor_request.id},
    )


def send_food_dept_alert_email(db: Session, visitor_request: VisitorRequest) -> None:
    from app.core.enums import RoleKey
    from app.models.rbac import Role, User as UserModel, UserRole

    rows = (
        db.execute(
            select(UserModel.email)
            .join(UserRole, UserRole.user_id == UserModel.id)
            .join(Role, Role.id == UserRole.role_id)
            .where(
                Role.key.in_([RoleKey.HR.value, RoleKey.ADMIN.value]),
                UserModel.is_active.is_(True),
            )
        )
        .scalars()
        .all()
    )
    recipients = [r for r in rows if r]
    if not recipients:
        return
    subject = f"Meal request — {visitor_request.visitor_name} on {visitor_request.visit_date.isoformat()}"
    text = "\n".join(
        [
            "A visitor request needs meal arrangements.",
            f"Request: {visitor_request.request_no}",
            f"Visitor: {visitor_request.visitor_name} ({visitor_request.company_name or '-'})",
            f"Visit Date: {visitor_request.visit_date.isoformat()}",
            f"Visit Time: {visitor_request.visit_time.strftime('%H:%M') if visitor_request.visit_time else 'TBD'}",
        ]
    )
    send_bulk_email(
        db,
        event_type="food_dept_alert_email",
        recipients=recipients,
        subject=subject,
        text_body=text,
        html_body=text.replace("\n", "<br/>"),
        payload={"request_id": visitor_request.id},
    )


def send_hospitality_status_email(db: Session, hospitality, new_status: str) -> None:
    vr = hospitality.visitor_request
    if not vr or not vr.host_user or not vr.host_user.email:
        return
    subject = f"Hospitality update — {vr.visitor_name}: {new_status.replace('_', ' ')}"
    text = "\n".join(
        [
            f"Hospitality logistics for {vr.visitor_name} are now: {new_status}.",
            f"Request: {vr.request_no}",
            f"Visit Date: {vr.visit_date.isoformat()}",
            "",
            "Open the VMS Hospitality console for details.",
        ]
    )
    send_bulk_email(
        db,
        event_type="hospitality_status_email",
        recipients=[vr.host_user.email],
        subject=subject,
        text_body=text,
        html_body=text.replace("\n", "<br/>"),
        payload={"hospitality_id": hospitality.id, "request_id": vr.id, "new_status": new_status},
    )


def send_visitor_approval_email(db: Session, visitor_request: VisitorRequest) -> None:
    recipient_email = settings.visitor_approval_test_email or visitor_request.email
    if not recipient_email:
        return

    notification = Notification(
        recipient_user_id=None,
        channel=NotificationChannel.EMAIL,
        event_type="visitor_approval_email",
        title=f"Visitor approval email for {visitor_request.request_no}",
        message=f"Approval QR sent to {recipient_email}",
        status=NotificationStatus.PENDING,
        payload_json={
            "request_id": visitor_request.id,
            "visitor_email": visitor_request.email,
            "recipient_email": recipient_email,
            "test_override_enabled": bool(settings.visitor_approval_test_email),
        },
    )
    db.add(notification)
    db.flush()

    try:
        qr_png = _build_qr_png(visitor_request.badge.qr_code_value if visitor_request.badge else visitor_request.qr_code_value or "")
        message = _build_approval_email(visitor_request, qr_png, recipient_email)
        _send_message(message)
        notification.status = NotificationStatus.SENT
    except Exception as exc:
        notification.status = NotificationStatus.FAILED
        notification.payload_json = {
            **(notification.payload_json or {}),
            "error": str(exc),
        }
        logger.exception("Failed to send visitor approval email for request %s", visitor_request.request_no)
    finally:
        db.add(notification)
        db.flush()
