"""create initial schema

Revision ID: 49e677d8cab
Revises: 
Create Date: 2015-07-20 12:43:53.913625

"""

# revision identifiers, used by Alembic.
revision = '49e677d8cab'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sapg

def upgrade():
    # Create tables
    op.create_table(
        'components',
        sa.Column('id', sa.Integer, primary_key=True, unique=True,
            nullable=False),
        sa.Column('code', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('datasheet_url', sa.Text),
        sa.Column('created_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, unique=True,
            nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    permission_enum = sapg.ENUM(
        'create', 'read', 'update', 'delete',
        name='permission'
    )

    op.create_table(
        'user_component_perms',
        sa.Column('id', sa.Integer, primary_key=True, unique=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'),
            nullable=False),
        sa.Column('component_id', sa.Integer, sa.ForeignKey('components.id'),
            nullable=False),
        sa.Column('permission', permission_enum, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # If this were anything other than the base migration, this is how you'd
    # backfill rows.
    ## op.execute('UPDATE components SET updated_at=CURRENT_TIMESTAMP;')

    # Add a trigger to automatically update the updated_at column on update.
    op.execute('''
        CREATE FUNCTION update_updated_at_col() RETURNS TRIGGER AS '
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END
        ' LANGUAGE 'plpgsql';
    ''')

    op.execute('''
        CREATE TRIGGER update_components_updated_at_trigger
            BEFORE UPDATE ON components
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
    ''')

    op.execute('''
        CREATE TRIGGER update_users_updated_at_trigger
            BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
    ''')

def downgrade():
    op.drop_table('user_component_perms')
    op.drop_table('users')
    op.drop_table('components')
    op.execute('DROP TYPE permission;')
    op.execute('DROP FUNCTION update_updated_at_col() CASCADE;')
