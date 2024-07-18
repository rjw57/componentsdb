"""create_updated_at_triggers

Revision ID: 660d48ec93c5
Revises: 9cce51e5ac43
Create Date: 2024-07-18 11:57:32.223870

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "660d48ec93c5"
down_revision: Union[str, None] = "9cce51e5ac43"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add a trigger to automatically update the updated_at column on update.
    op.execute(
        """
        CREATE FUNCTION update_updated_at_col() RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_cabinets_updated_at_trigger
            BEFORE UPDATE ON cabinets
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_components_updated_at_trigger
            BEFORE UPDATE ON components
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_drawers_updated_at_trigger
            BEFORE UPDATE ON drawers
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
        """
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION update_updated_at_col() CASCADE;")
