"""emergency module tables

Revision ID: 20260427_0002
Revises: 20260331_0001
Create Date: 2026-04-27 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260427_0002"
down_revision = "20260331_0001"
branch_labels = None
depends_on = None


emergency_type_enum = sa.Enum(
    "fire", "medical", "security", "disaster", "other", name="emergency_type_enum"
)
emergency_severity_enum = sa.Enum(
    "low", "medium", "high", "critical", name="emergency_severity_enum"
)
emergency_status_enum = sa.Enum(
    "active", "contained", "resolved", name="emergency_status_enum"
)
muster_status_enum = sa.Enum(
    "pending", "accounted_for", "unaccounted", "evacuated", name="muster_status_enum"
)


def _ref(enum: sa.Enum) -> sa.Enum:
    """Reference an existing enum type without re-creating it inside create_table."""
    return sa.Enum(name=enum.name, create_type=False, _create_events=False)


def upgrade() -> None:
    bind = op.get_bind()
    emergency_type_enum.create(bind, checkfirst=True)
    emergency_severity_enum.create(bind, checkfirst=True)
    emergency_status_enum.create(bind, checkfirst=True)
    muster_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "emergency_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_no", sa.String(length=40), nullable=False),
        sa.Column("event_type", _ref(emergency_type_enum), nullable=False),
        sa.Column("severity", _ref(emergency_severity_enum), nullable=False, server_default="medium"),
        sa.Column("status", _ref(emergency_status_enum), nullable=False, server_default="active"),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("triggered_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolved_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("event_no"),
    )
    op.create_index("ix_emergency_events_event_no", "emergency_events", ["event_no"], unique=True)
    op.create_index("ix_emergency_events_event_type", "emergency_events", ["event_type"])
    op.create_index("ix_emergency_events_status", "emergency_events", ["status"])

    op.create_table(
        "evacuation_musters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "emergency_event_id",
            sa.Integer(),
            sa.ForeignKey("emergency_events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "visitor_request_id",
            sa.Integer(),
            sa.ForeignKey("visitor_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("visitor_name_snapshot", sa.String(length=120), nullable=False),
        sa.Column("host_name_snapshot", sa.String(length=120), nullable=True),
        sa.Column("status", _ref(muster_status_enum), nullable=False, server_default="pending"),
        sa.Column("accounted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "accounted_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_evacuation_musters_event", "evacuation_musters", ["emergency_event_id"])
    op.create_index("ix_evacuation_musters_visitor", "evacuation_musters", ["visitor_request_id"])
    op.create_index("ix_evacuation_musters_status", "evacuation_musters", ["status"])

    op.create_table(
        "health_screenings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "visitor_request_id",
            sa.Integer(),
            sa.ForeignKey("visitor_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("temperature_celsius", sa.Float(), nullable=True),
        sa.Column("has_symptoms", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("symptom_notes", sa.Text(), nullable=True),
        sa.Column("cleared", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "screened_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_health_screenings_visitor", "health_screenings", ["visitor_request_id"])

    op.create_table(
        "contact_trace_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "source_visitor_request_id",
            sa.Integer(),
            sa.ForeignKey("visitor_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "contact_visitor_request_id",
            sa.Integer(),
            sa.ForeignKey("visitor_requests.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "contact_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("contact_name", sa.String(length=120), nullable=True),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("contact_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "recorded_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_contact_trace_source", "contact_trace_records", ["source_visitor_request_id"]
    )
    op.create_index(
        "ix_contact_trace_contact", "contact_trace_records", ["contact_visitor_request_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_contact_trace_contact", table_name="contact_trace_records")
    op.drop_index("ix_contact_trace_source", table_name="contact_trace_records")
    op.drop_table("contact_trace_records")
    op.drop_index("ix_health_screenings_visitor", table_name="health_screenings")
    op.drop_table("health_screenings")
    op.drop_index("ix_evacuation_musters_status", table_name="evacuation_musters")
    op.drop_index("ix_evacuation_musters_visitor", table_name="evacuation_musters")
    op.drop_index("ix_evacuation_musters_event", table_name="evacuation_musters")
    op.drop_table("evacuation_musters")
    op.drop_index("ix_emergency_events_status", table_name="emergency_events")
    op.drop_index("ix_emergency_events_event_type", table_name="emergency_events")
    op.drop_index("ix_emergency_events_event_no", table_name="emergency_events")
    op.drop_table("emergency_events")
    bind = op.get_bind()
    muster_status_enum.drop(bind, checkfirst=True)
    emergency_status_enum.drop(bind, checkfirst=True)
    emergency_severity_enum.drop(bind, checkfirst=True)
    emergency_type_enum.drop(bind, checkfirst=True)
