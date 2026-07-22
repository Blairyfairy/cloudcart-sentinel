"""initial schema"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "monitored_services",
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("kind", sa.String(24), nullable=False),
        sa.Column("target", sa.String(2048), nullable=False),
        sa.Column("interval_seconds", sa.Integer(), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("slo_target", sa.Float(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_monitored_services"),
        sa.UniqueConstraint("name", name="uq_monitored_services_name"),
    )
    op.create_index("ix_monitored_services_name", "monitored_services", ["name"])
    op.create_table(
        "probe_results",
        sa.Column("service_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["monitored_services.id"], ondelete="CASCADE", name="fk_probe_results_service_id_monitored_services"),
        sa.PrimaryKeyConstraint("id", name="pk_probe_results"),
    )
    op.create_index("ix_probe_results_service_id", "probe_results", ["service_id"])
    op.create_index("ix_probe_results_started_at", "probe_results", ["started_at"])
    op.create_index("ix_probe_results_status", "probe_results", ["status"])

def downgrade():
    op.drop_table("probe_results")
    op.drop_table("monitored_services")
