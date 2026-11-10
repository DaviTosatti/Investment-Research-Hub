"""preserve statement originals and versioned import previews

Revision ID: c47fb0c93e44
Revises: 0002_ledger_integrity
"""

import sqlalchemy as sa
from alembic import op

revision = "c47fb0c93e44"
down_revision = "0002_ledger_integrity"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "data_sources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("name_key", sa.String(length=120), nullable=False),
        sa.Column("kind", sa.String(length=24), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name_key"),
    )
    op.create_table(
        "original_files",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sha256"),
    )
    op.create_table(
        "import_batches",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("portfolio_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("original_id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=180), nullable=False),
        sa.Column("parse_key", sa.String(length=64), nullable=False),
        sa.Column("parse_options", sa.JSON(), nullable=False),
        sa.Column("table", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["original_id"],
            ["original_files.id"],
        ),
        sa.ForeignKeyConstraint(
            ["portfolio_id"],
            ["portfolios.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["data_sources.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("portfolio_id", "source_id", "original_id", "parse_key"),
    )
    op.create_index(
        op.f("ix_import_batches_portfolio_id"), "import_batches", ["portfolio_id"], unique=False
    )
    op.create_table(
        "import_previews",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("import_id", sa.String(length=36), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("ledger_version", sa.String(length=64), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("rows", sa.JSON(), nullable=False),
        sa.Column("summary", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["import_id"],
            ["import_batches.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("import_id", "revision"),
    )
    op.create_index(
        op.f("ix_import_previews_import_id"), "import_previews", ["import_id"], unique=False
    )
    op.create_table(
        "import_receipts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("import_id", sa.String(length=36), nullable=False),
        sa.Column("preview_id", sa.String(length=36), nullable=False),
        sa.Column("results", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["import_id"],
            ["import_batches.id"],
        ),
        sa.ForeignKeyConstraint(
            ["preview_id"],
            ["import_previews.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("import_id"),
        sa.UniqueConstraint("preview_id"),
    )
    for table in (
        "data_sources",
        "original_files",
        "import_batches",
        "import_previews",
        "import_receipts",
    ):
        op.execute(f"""
            CREATE TRIGGER hub_immutable BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION hub_reject_history_mutation()
        """)


def downgrade():
    op.drop_table("import_receipts")
    op.drop_index(op.f("ix_import_previews_import_id"), table_name="import_previews")
    op.drop_table("import_previews")
    op.drop_index(op.f("ix_import_batches_portfolio_id"), table_name="import_batches")
    op.drop_table("import_batches")
    op.drop_table("original_files")
    op.drop_table("data_sources")
