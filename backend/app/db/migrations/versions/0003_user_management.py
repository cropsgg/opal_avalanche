"""Add user management tables

Revision ID: 0003_user_management
Revises: 0002_security_and_compliance
Create Date: 2024-12-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003_user_management'
down_revision = '0002_security_and_compliance'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('clerk_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=True, default='lawyer'),
        sa.Column('wallet_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, default=sa.text('now()')),
        sa.CheckConstraint("role in ('lawyer', 'admin', 'paralegal', 'client')", name='users_role_chk'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clerk_id')
    )
    op.create_index('ix_users_clerk_id', 'users', ['clerk_id'])

    # Create firms table
    op.create_table('firms',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('gstin', sa.String(), nullable=True),
        sa.Column('pan', sa.String(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('pincode', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_firms junction table
    op.create_table('user_firms',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('firm_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(), nullable=True, default='member'),
        sa.Column('joined_at', sa.TIMESTAMP(timezone=True), nullable=False, default=sa.text('now()')),
        sa.CheckConstraint("role in ('owner', 'partner', 'associate', 'member', 'intern')", name='user_firms_role_chk'),
        sa.ForeignKeyConstraint(['firm_id'], ['firms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'firm_id')
    )

    # Add foreign key constraint to existing matters table
    op.add_column('matters', sa.Column('user_id_new', postgresql.UUID(as_uuid=True), nullable=True))
    
    # For existing matters, we'll need to handle the migration carefully
    # Since there might be existing data, we'll make the new column nullable first
    # and then handle the data migration separately if needed
    
    # Drop the old user_id column and rename the new one
    op.drop_column('matters', 'user_id')
    op.alter_column('matters', 'user_id_new', new_column_name='user_id', nullable=False)
    op.create_foreign_key('fk_matters_user_id', 'matters', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # Add foreign key constraint to existing billing_accounts table
    op.add_column('billing_accounts', sa.Column('user_id_new', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Drop the old user_id column and rename the new one
    op.drop_column('billing_accounts', 'user_id')
    op.alter_column('billing_accounts', 'user_id_new', new_column_name='user_id', nullable=False)
    op.create_foreign_key('fk_billing_accounts_user_id', 'billing_accounts', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # Create updated_at trigger for users table
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    op.execute("""
        CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_firms_updated_at BEFORE UPDATE ON firms
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users;")
    op.execute("DROP TRIGGER IF EXISTS update_firms_updated_at ON firms;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Remove foreign key constraints
    op.drop_constraint('fk_matters_user_id', 'matters', type_='foreignkey')
    op.drop_constraint('fk_billing_accounts_user_id', 'billing_accounts', type_='foreignkey')

    # Restore original user_id columns (this is a destructive operation)
    op.alter_column('matters', 'user_id', type_=postgresql.UUID(as_uuid=True), nullable=False)
    op.alter_column('billing_accounts', 'user_id', type_=postgresql.UUID(as_uuid=True), nullable=False)

    # Drop user management tables
    op.drop_table('user_firms')
    op.drop_table('firms')
    op.drop_index('ix_users_clerk_id')
    op.drop_table('users')
