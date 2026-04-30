"""initial schema

Revision ID: 20260331_0001
Revises:
Create Date: 2026-03-31 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260331_0001"
down_revision = None
branch_labels = None
depends_on = None


visitor_type_enum = sa.Enum("supplier", "candidate", "contractor", "customer", "vip_customer", name="visitor_type_enum")
visitor_request_status_enum = sa.Enum(
    "draft",
    "scheduled",
    "pending_manager_approval",
    "pending_hod_approval",
    "pending_ceo_office_approval",
    "pending_security_clearance",
    "pending_it_approval",
    "pending_logistics_confirmation",
    "approved",
    "rejected",
    "sent_back",
    "cancelled",
    "checked_in",
    "checked_out",
    name="visitor_request_status_enum",
)
approval_step_status_enum = sa.Enum(
    "queued", "active", "approved", "rejected", "sent_back", "cancelled", "skipped", name="approval_step_status_enum"
)
approval_action_type_enum = sa.Enum(
    "submit", "approve", "reject", "send_back", "cancel", "check_in", "check_out", "security_alert", name="approval_action_type_enum"
)
badge_status_enum = sa.Enum("generated", "issued", "returned", "void", name="badge_status_enum")
gate_action_enum = sa.Enum("scan", "check_in", "check_out", "access_blocked", "access_warning", name="gate_action_enum")
blacklist_action_type_enum = sa.Enum("block", "alert", "allow_with_warning", name="blacklist_action_type_enum")
notification_channel_enum = sa.Enum("email", "system", "sms", "whatsapp", name="notification_channel_enum")
notification_status_enum = sa.Enum("pending", "sent", "failed", "read", name="notification_status_enum")


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_departments_id"), "departments", ["id"], unique=False)

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("key"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_roles_id"), "roles", ["id"], unique=False)
    op.create_index(op.f("ix_roles_key"), "roles", ["key"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_code", sa.String(length=40), nullable=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("mobile", sa.String(length=20), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("department_id", sa.Integer(), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("employee_code"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_employee_code"), "users", ["employee_code"], unique=False)

    op.create_table(
        "user_roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),
    )
    op.create_index(op.f("ix_user_roles_user_id"), "user_roles", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_roles_role_id"), "user_roles", ["role_id"], unique=False)

    op.create_table(
        "visitor_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_no", sa.String(length=32), nullable=False),
        sa.Column("visitor_type", visitor_type_enum, nullable=False),
        sa.Column("request_date", sa.Date(), nullable=False),
        sa.Column("visit_date", sa.Date(), nullable=False),
        sa.Column("visit_time", sa.Time(), nullable=True),
        sa.Column("requested_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("department_id", sa.Integer(), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("host_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("visitor_name", sa.String(length=120), nullable=False),
        sa.Column("company_name", sa.String(length=160), nullable=True),
        sa.Column("mobile", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("id_proof_type", sa.String(length=80), nullable=True),
        sa.Column("id_proof_number", sa.String(length=80), nullable=True),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("status", visitor_request_status_enum, nullable=False, server_default="draft"),
        sa.Column("current_approval_level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("requires_security_clearance", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("requires_it_access", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("requires_hospitality", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("badge_no", sa.String(length=40), nullable=True),
        sa.Column("qr_code_value", sa.String(length=120), nullable=True),
        sa.Column("is_id_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("check_in_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("check_out_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("badge_no"),
        sa.UniqueConstraint("qr_code_value"),
        sa.UniqueConstraint("request_no"),
    )
    for index in [
        "id",
        "request_no",
        "visitor_type",
        "visit_date",
        "visitor_name",
        "mobile",
        "email",
        "id_proof_number",
        "status",
    ]:
        op.create_index(f"ix_visitor_requests_{index}", "visitor_requests", [index], unique=False)

    op.create_table(
        "visitor_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("visitor_request_id", sa.Integer(), sa.ForeignKey("visitor_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(length=80), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("uploaded_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("visitor_request_id", sa.Integer(), sa.ForeignKey("visitor_requests.id", ondelete="CASCADE"), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("uploaded_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_attachments_entity_type"), "attachments", ["entity_type"], unique=False)
    op.create_index(op.f("ix_attachments_entity_id"), "attachments", ["entity_id"], unique=False)

    op.create_table(
        "visitor_badges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("visitor_request_id", sa.Integer(), sa.ForeignKey("visitor_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("badge_no", sa.String(length=40), nullable=False),
        sa.Column("qr_code_value", sa.String(length=120), nullable=False),
        sa.Column("status", badge_status_enum, nullable=False, server_default="generated"),
        sa.Column("printed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("visitor_request_id"),
        sa.UniqueConstraint("badge_no"),
        sa.UniqueConstraint("qr_code_value"),
    )
    op.create_index(op.f("ix_visitor_badges_badge_no"), "visitor_badges", ["badge_no"], unique=False)
    op.create_index(op.f("ix_visitor_badges_qr_code_value"), "visitor_badges", ["qr_code_value"], unique=False)

    op.create_table(
        "visitor_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("visitor_request_id", sa.Integer(), sa.ForeignKey("visitor_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", gate_action_enum, nullable=False),
        sa.Column("gate_entry_point", sa.String(length=120), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("performed_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_visitor_logs_action"), "visitor_logs", ["action"], unique=False)
    op.create_index(op.f("ix_visitor_logs_visitor_request_id"), "visitor_logs", ["visitor_request_id"], unique=False)

    op.create_table(
        "visitor_zones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_visitor_zones_code"), "visitor_zones", ["code"], unique=False)

    op.create_table(
        "hospitality_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("visitor_request_id", sa.Integer(), sa.ForeignKey("visitor_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("meal_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("transport_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("meeting_room", sa.String(length=120), nullable=True),
        sa.Column("escort_needed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("vip_notes", sa.Text(), nullable=True),
        sa.Column("logistics_status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("visitor_request_id"),
    )

    op.create_table(
        "interview_panel_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("visitor_request_id", sa.Integer(), sa.ForeignKey("visitor_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("panel_member_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_interview_panel_members_visitor_request_id"), "interview_panel_members", ["visitor_request_id"], unique=False)

    op.create_table(
        "approval_steps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("visitor_request_id", sa.Integer(), sa.ForeignKey("visitor_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("step_key", sa.String(length=80), nullable=False),
        sa.Column("step_name", sa.String(length=120), nullable=False),
        sa.Column("role_key", sa.String(length=50), nullable=False),
        sa.Column("assigned_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("pending_status", sa.String(length=80), nullable=False),
        sa.Column("status", approval_step_status_enum, nullable=False, server_default="queued"),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_approval_steps_visitor_request_id"), "approval_steps", ["visitor_request_id"], unique=False)
    op.create_index(op.f("ix_approval_steps_step_order"), "approval_steps", ["step_order"], unique=False)
    op.create_index(op.f("ix_approval_steps_role_key"), "approval_steps", ["role_key"], unique=False)

    op.create_table(
        "approval_actions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("visitor_request_id", sa.Integer(), sa.ForeignKey("visitor_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("approval_step_id", sa.Integer(), sa.ForeignKey("approval_steps.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", approval_action_type_enum, nullable=False),
        sa.Column("action_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("from_status", sa.String(length=80), nullable=True),
        sa.Column("to_status", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_approval_actions_visitor_request_id"), "approval_actions", ["visitor_request_id"], unique=False)

    op.create_table(
        "visitor_blacklist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("visitor_name", sa.String(length=120), nullable=False),
        sa.Column("mobile", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("id_proof_type", sa.String(length=80), nullable=True),
        sa.Column("id_proof_number", sa.String(length=80), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("action_type", blacklist_action_type_enum, nullable=False, server_default="block"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("added_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    for index in ["visitor_name", "mobile", "email", "id_proof_number"]:
        op.create_index(f"ix_visitor_blacklist_{index}", "visitor_blacklist", [index], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipient_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("channel", notification_channel_enum, nullable=False, server_default="system"),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", notification_status_enum, nullable=False, server_default="pending"),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_notifications_recipient_user_id"), "notifications", ["recipient_user_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("details_json", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    for index in ["entity_type", "entity_id", "action"]:
        op.create_index(f"ix_audit_logs_{index}", "audit_logs", [index], unique=False)

    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("value_type", sa.String(length=40), nullable=False, server_default="string"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("key"),
    )
    op.create_index(op.f("ix_app_settings_key"), "app_settings", ["key"], unique=False)


def downgrade() -> None:
    for table in [
        "app_settings",
        "audit_logs",
        "notifications",
        "visitor_blacklist",
        "approval_actions",
        "approval_steps",
        "interview_panel_members",
        "hospitality_requests",
        "visitor_zones",
        "visitor_logs",
        "visitor_badges",
        "attachments",
        "visitor_documents",
        "visitor_requests",
        "user_roles",
        "users",
        "roles",
        "departments",
    ]:
        op.drop_table(table)

    notification_status_enum.drop(op.get_bind(), checkfirst=False)
    notification_channel_enum.drop(op.get_bind(), checkfirst=False)
    blacklist_action_type_enum.drop(op.get_bind(), checkfirst=False)
    gate_action_enum.drop(op.get_bind(), checkfirst=False)
    badge_status_enum.drop(op.get_bind(), checkfirst=False)
    approval_action_type_enum.drop(op.get_bind(), checkfirst=False)
    approval_step_status_enum.drop(op.get_bind(), checkfirst=False)
    visitor_request_status_enum.drop(op.get_bind(), checkfirst=False)
    visitor_type_enum.drop(op.get_bind(), checkfirst=False)
