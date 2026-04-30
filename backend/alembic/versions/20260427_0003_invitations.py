"""visitor invitations

Revision ID: 20260427_0003
Revises: 20260427_0002
Create Date: 2026-04-27 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260427_0003"
down_revision = "20260427_0002"
branch_labels = None
depends_on = None


invitation_status_enum = sa.Enum(
    "pending", "used", "expired", "cancelled", name="invitation_status_enum"
)


def upgrade() -> None:
    bind = op.get_bind()
    invitation_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "visitor_invitations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("host_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("department_id", sa.Integer(), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("visitor_name", sa.String(length=120), nullable=False),
        sa.Column("visitor_email", sa.String(length=255), nullable=True),
        sa.Column("visitor_mobile", sa.String(length=20), nullable=True),
        sa.Column("company_name", sa.String(length=160), nullable=True),
        sa.Column(
            "visitor_type",
            sa.Enum(name="visitor_type_enum", create_type=False, _create_events=False),
            nullable=False,
        ),
        sa.Column("visit_date", sa.Date(), nullable=False),
        sa.Column("visit_time", sa.Time(), nullable=True),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum(name="invitation_status_enum", create_type=False, _create_events=False),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "visitor_request_id",
            sa.Integer(),
            sa.ForeignKey("visitor_requests.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_visitor_invitations_token", "visitor_invitations", ["token"], unique=True)
    op.create_index("ix_visitor_invitations_host", "visitor_invitations", ["host_user_id"])
    op.create_index("ix_visitor_invitations_visit_date", "visitor_invitations", ["visit_date"])
    op.create_index("ix_visitor_invitations_status", "visitor_invitations", ["status"])


def downgrade() -> None:
    op.drop_index("ix_visitor_invitations_status", table_name="visitor_invitations")
    op.drop_index("ix_visitor_invitations_visit_date", table_name="visitor_invitations")
    op.drop_index("ix_visitor_invitations_host", table_name="visitor_invitations")
    op.drop_index("ix_visitor_invitations_token", table_name="visitor_invitations")
    op.drop_table("visitor_invitations")
    bind = op.get_bind()
    invitation_status_enum.drop(bind, checkfirst=True)
