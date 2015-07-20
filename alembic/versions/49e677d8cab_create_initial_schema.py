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
    # Create table
    op.create_table(
        'components',
        sa.Column('id', sa.Integer, primary_key=True, unique=True, nullable=False),
        sa.Column('code', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('datasheet_url', sa.Text),
        sa.Column('created_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Backfill any existing rows. (Should be NOP but add for documentation.)
    op.execute('UPDATE components SET updated_at=CURRENT_TIMESTAMP;')

    # Add a trigger to automatically update the updated_at column on update.
    op.execute('''
        CREATE FUNCTION update_components_updated_at_col() RETURNS TRIGGER AS '
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END
        ' LANGUAGE 'plpgsql';
    ''')

    op.execute('''
        CREATE TRIGGER update_components_updated_at_trigger
            BEFORE UPDATE ON components
            FOR EACH ROW EXECUTE PROCEDURE update_components_updated_at_col()
        ;
    ''')

def downgrade():
    op.drop_table('components')
    op.execute('DROP FUNCTION update_components_updated_at_col() CASCADE;')
