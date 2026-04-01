from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr
from io import BytesIO

import qrcode
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
