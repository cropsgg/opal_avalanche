"""Security and compliance features

Revision ID: 0002_security_and_compliance
Revises: 0001_init
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON


# revision identifiers, used by Alembic.
revision = '0002_security_and_compliance'
down_revision = '0001_init'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add security and compliance features"""
    
    # Add encrypted message column to queries table
    op.add_column('queries', sa.Column('message_encrypted', JSON, nullable=True))
    
    # Create PII tracking table
    op.create_table('pii_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('query_id', UUID(as_uuid=True), nullable=True),
        sa.Column('document_id', UUID(as_uuid=True), nullable=True),
        sa.Column('pii_type', sa.String(), nullable=False),
        sa.Column('detection_confidence', sa.Numeric(), server_default='1.0'),
        sa.Column('redacted_count', sa.Integer(), server_default='1'),
        sa.Column('original_encrypted', JSON, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['query_id'], ['queries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )
    
    # Create data retention log table
    op.create_table('data_retention_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('retention_type', sa.String(), nullable=False),
        sa.Column('table_name', sa.String(), nullable=False),
        sa.Column('record_id', sa.String(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('retention_period_days', sa.Integer(), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('metadata_json', JSON, server_default='{}'),
    )
    
    # Create indexes for performance
    op.create_index('idx_pii_records_user_id', 'pii_records', ['user_id'])
    op.create_index('idx_pii_records_query_id', 'pii_records', ['query_id'])
    op.create_index('idx_pii_records_type', 'pii_records', ['pii_type'])
    op.create_index('idx_pii_records_created_at', 'pii_records', ['created_at'])
    
    op.create_index('idx_retention_logs_user_id', 'data_retention_logs', ['user_id'])
    op.create_index('idx_retention_logs_table', 'data_retention_logs', ['table_name'])
    op.create_index('idx_retention_logs_deleted_at', 'data_retention_logs', ['deleted_at'])
    
    # Enable Row Level Security on user-specific tables
    op.execute("ALTER TABLE matters ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE documents ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE queries ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE runs ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE billing_accounts ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE billing_ledger ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE pii_records ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE data_retention_logs ENABLE ROW LEVEL SECURITY;")
    
    # Create function to get current user from application context
    op.execute("""
        CREATE OR REPLACE FUNCTION auth.current_user_id() RETURNS UUID AS $$
        BEGIN
            -- Get user ID from current session variable set by application
            RETURN NULLIF(current_setting('app.current_user_id', true), '')::UUID;
        EXCEPTION
            WHEN OTHERS THEN
                RETURN NULL;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)
    
    # Create RLS policies for multi-tenant isolation
    
    # Matters - users can only access their own matters
    op.execute("""
        CREATE POLICY matters_user_policy ON matters 
        FOR ALL 
        USING (user_id = auth.current_user_id());
    """)
    
    # Documents - users can only access documents they uploaded or that belong to their matters
    op.execute("""
        CREATE POLICY documents_user_policy ON documents 
        FOR ALL 
        USING (
            uploaded_by = auth.current_user_id() 
            OR matter_id IN (
                SELECT id FROM matters WHERE user_id = auth.current_user_id()
            )
        );
    """)
    
    # Queries - users can only access queries from their matters
    op.execute("""
        CREATE POLICY queries_user_policy ON queries 
        FOR ALL 
        USING (
            matter_id IN (
                SELECT id FROM matters WHERE user_id = auth.current_user_id()
            )
        );
    """)
    
    # Runs - users can only access runs from their queries
    op.execute("""
        CREATE POLICY runs_user_policy ON runs 
        FOR ALL 
        USING (
            query_id IN (
                SELECT q.id FROM queries q 
                JOIN matters m ON q.matter_id = m.id 
                WHERE m.user_id = auth.current_user_id()
            )
        );
    """)
    
    # Billing accounts - users can only access their own billing
    op.execute("""
        CREATE POLICY billing_accounts_user_policy ON billing_accounts 
        FOR ALL 
        USING (user_id = auth.current_user_id());
    """)
    
    # Billing ledger - users can only access their own transactions
    op.execute("""
        CREATE POLICY billing_ledger_user_policy ON billing_ledger 
        FOR ALL 
        USING (user_id = auth.current_user_id());
    """)
    
    # PII records - users can only access their own PII audit logs
    op.execute("""
        CREATE POLICY pii_records_user_policy ON pii_records 
        FOR ALL 
        USING (user_id = auth.current_user_id());
    """)
    
    # Data retention logs - users can only access their own retention logs
    op.execute("""
        CREATE POLICY retention_logs_user_policy ON data_retention_logs 
        FOR ALL 
        USING (user_id = auth.current_user_id());
    """)
    
    # Agent votes - users can only access votes from their runs
    op.execute("""
        CREATE POLICY agent_votes_user_policy ON agent_votes 
        FOR ALL 
        USING (
            run_id IN (
                SELECT r.id FROM runs r
                JOIN queries q ON r.query_id = q.id
                JOIN matters m ON q.matter_id = m.id 
                WHERE m.user_id = auth.current_user_id()
            )
        );
    """)
    
    # Onchain proofs - users can only access proofs from their runs
    op.execute("""
        CREATE POLICY onchain_proofs_user_policy ON onchain_proofs 
        FOR ALL 
        USING (
            run_id IN (
                SELECT r.id FROM runs r
                JOIN queries q ON r.query_id = q.id
                JOIN matters m ON q.matter_id = m.id 
                WHERE m.user_id = auth.current_user_id()
            )
        );
    """)
    
    # Add constraint to ensure retention type is valid
    op.execute("""
        ALTER TABLE data_retention_logs 
        ADD CONSTRAINT check_retention_type 
        CHECK (retention_type IN ('soft_delete', 'hard_delete', 'crypto_shred'));
    """)
    
    # Add constraint to ensure retention reason is valid
    op.execute("""
        ALTER TABLE data_retention_logs 
        ADD CONSTRAINT check_retention_reason 
        CHECK (reason IN ('retention_policy', 'user_request', 'compliance', 'gdpr_right_to_be_forgotten'));
    """)


def downgrade() -> None:
    """Remove security and compliance features"""
    
    # Drop RLS policies
    op.execute("DROP POLICY IF EXISTS matters_user_policy ON matters;")
    op.execute("DROP POLICY IF EXISTS documents_user_policy ON documents;")
    op.execute("DROP POLICY IF EXISTS queries_user_policy ON queries;")
    op.execute("DROP POLICY IF EXISTS runs_user_policy ON runs;")
    op.execute("DROP POLICY IF EXISTS billing_accounts_user_policy ON billing_accounts;")
    op.execute("DROP POLICY IF EXISTS billing_ledger_user_policy ON billing_ledger;")
    op.execute("DROP POLICY IF EXISTS pii_records_user_policy ON pii_records;")
    op.execute("DROP POLICY IF EXISTS retention_logs_user_policy ON data_retention_logs;")
    op.execute("DROP POLICY IF EXISTS agent_votes_user_policy ON agent_votes;")
    op.execute("DROP POLICY IF EXISTS onchain_proofs_user_policy ON onchain_proofs;")
    
    # Disable RLS
    op.execute("ALTER TABLE matters DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE documents DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE queries DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE runs DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE billing_accounts DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE billing_ledger DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE pii_records DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE data_retention_logs DISABLE ROW LEVEL SECURITY;")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS auth.current_user_id();")
    
    # Drop indexes
    op.drop_index('idx_pii_records_user_id')
    op.drop_index('idx_pii_records_query_id')
    op.drop_index('idx_pii_records_type')
    op.drop_index('idx_pii_records_created_at')
    op.drop_index('idx_retention_logs_user_id')
    op.drop_index('idx_retention_logs_table')
    op.drop_index('idx_retention_logs_deleted_at')
    
    # Drop tables
    op.drop_table('data_retention_logs')
    op.drop_table('pii_records')
    
    # Remove encrypted message column
    op.drop_column('queries', 'message_encrypted')
