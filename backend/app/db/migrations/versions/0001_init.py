from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Run raw schema SQL for parity with Supabase setup
    schema_sql = open("backend/app/db/schema.sql", "r", encoding="utf-8").read()
    op.execute(schema_sql)


def downgrade() -> None:
    op.execute("drop table if exists billing_ledger cascade;")
    op.execute("drop table if exists billing_accounts cascade;")
    op.execute("drop table if exists onchain_proofs cascade;")
    op.execute("drop table if exists agent_votes cascade;")
    op.execute("drop table if exists runs cascade;")
    op.execute("drop table if exists queries cascade;")
    op.execute("drop table if exists documents cascade;")
    op.execute("drop table if exists matters cascade;")
    op.execute("drop table if exists chunks cascade;")
    op.execute("drop table if exists authorities cascade;")


