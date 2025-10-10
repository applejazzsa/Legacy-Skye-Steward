from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250929_0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Enums
    handover_shift = sa.Enum("AM", "PM", name="shift_enum")
    handover_period = sa.Enum("BREAKFAST", "LUNCH", "DINNER", name="mealperiodenum")
    severity_enum = sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="severityenum")
    incident_status = sa.Enum("OPEN", "RESOLVED", name="incidentstatusenum")
    sentiment_enum = sa.Enum("VERY_HAPPY", "HAPPY", "NEUTRAL", "UNHAPPY", name="sentimentenum")

    if op.get_bind().dialect.name != "sqlite":
        handover_shift.create(op.get_bind(), checkfirst=True)
        handover_period.create(op.get_bind(), checkfirst=True)
        severity_enum.create(op.get_bind(), checkfirst=True)
        incident_status.create(op.get_bind(), checkfirst=True)
        sentiment_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "handovers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("outlet", sa.String(length=100), index=True, nullable=False),
        sa.Column("date", sa.DateTime, index=True, nullable=False),
        sa.Column("shift", handover_shift if op.get_bind().dialect.name != "sqlite" else sa.String(10), index=True, nullable=False),
        sa.Column("period", handover_period if op.get_bind().dialect.name != "sqlite" else sa.String(20), index=True, nullable=False),
        sa.Column("bookings", sa.Integer, nullable=False, server_default="0"),
        sa.Column("walk_ins", sa.Integer, nullable=False, server_default="0"),
        sa.Column("covers", sa.Integer, nullable=False, server_default="0"),
        sa.Column("food_revenue", sa.Float, nullable=False, server_default="0"),
        sa.Column("beverage_revenue", sa.Float, nullable=False, server_default="0"),
        sa.Column("top_sales_csv", sa.Text, nullable=False, server_default=""),
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("outlet", sa.String(length=100), index=True, nullable=False),
        sa.Column("date", sa.DateTime, index=True, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("severity", severity_enum if op.get_bind().dialect.name != "sqlite" else sa.String(12), index=True, nullable=False),
        sa.Column("owner", sa.String(length=100)),
        sa.Column("status", incident_status if op.get_bind().dialect.name != "sqlite" else sa.String(10), index=True, nullable=False),
        sa.Column("action_taken", sa.Text),
        sa.Column("guest_reference", sa.String(length=100)),
    )

    op.create_table(
        "guest_notes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("outlet", sa.String(length=100), index=True, nullable=False),
        sa.Column("date", sa.DateTime, index=True, nullable=False),
        sa.Column("guest_name", sa.String(length=120)),
        sa.Column("room_number", sa.String(length=50)),
        sa.Column("occasion", sa.String(length=80)),
        sa.Column("note", sa.Text, nullable=False),
        sa.Column("sentiment", sentiment_enum if op.get_bind().dialect.name != "sqlite" else sa.String(20), index=True, nullable=False),
        sa.Column("staff_praised", sa.String(length=120)),
    )

def downgrade() -> None:
    op.drop_table("guest_notes")
    op.drop_table("incidents")
    op.drop_table("handovers")

    if op.get_bind().dialect.name != "sqlite":
        sa.Enum(name="sentimentenum").drop(op.get_bind(), checkfirst=True)
        sa.Enum(name="incidentstatusenum").drop(op.get_bind(), checkfirst=True)
        sa.Enum(name="severityenum").drop(op.get_bind(), checkfirst=True)
        sa.Enum(name="mealperiodenum").drop(op.get_bind(), checkfirst=True)
        sa.Enum(name="shift_enum").drop(op.get_bind(), checkfirst=True)
