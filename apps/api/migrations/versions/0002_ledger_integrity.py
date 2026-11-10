"""Protect event history and require balanced journal entries at commit."""

from alembic import op

revision = "0002_ledger_integrity"
down_revision = "fde27e01f059"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE FUNCTION hub_reject_history_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'History is append-only; use a versioned correction';
        END;
        $$ LANGUAGE plpgsql
    """)
    for table in ("transactions", "journal_entries", "prices", "audit_events"):
        op.execute(f"""
            CREATE TRIGGER hub_immutable BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION hub_reject_history_mutation()
        """)
    op.execute("""
        CREATE FUNCTION hub_check_journal_balance() RETURNS trigger AS $$
        DECLARE target_id varchar(36); entry_count bigint; balance numeric;
        BEGIN
            IF TG_TABLE_NAME = 'transactions' THEN target_id := NEW.id;
            ELSE target_id := NEW.transaction_id; END IF;
            SELECT count(*), coalesce(sum(amount),0) INTO entry_count, balance
                FROM journal_entries WHERE transaction_id = target_id;
            IF entry_count = 0 OR balance <> 0 THEN
                RAISE EXCEPTION 'Transaction requires a balanced journal';
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql
    """)
    for table in ("transactions", "journal_entries"):
        op.execute(f"""
            CREATE CONSTRAINT TRIGGER hub_balanced AFTER INSERT ON {table}
            DEFERRABLE INITIALLY DEFERRED FOR EACH ROW
            EXECUTE FUNCTION hub_check_journal_balance()
        """)


def downgrade():
    for table in ("transactions", "journal_entries"):
        op.execute(f"DROP TRIGGER hub_balanced ON {table}")
    op.execute("DROP FUNCTION hub_check_journal_balance()")
    for table in ("transactions", "journal_entries", "prices", "audit_events"):
        op.execute(f"DROP TRIGGER hub_immutable ON {table}")
    op.execute("DROP FUNCTION hub_reject_history_mutation()")
