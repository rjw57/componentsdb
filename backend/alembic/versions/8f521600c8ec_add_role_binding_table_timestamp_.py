"""add_role_binding_table_timestamp_triggers

Revision ID: 8f521600c8ec
Revises: 9519290d3c95
Create Date: 2024-08-18 10:19:32.868406

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8f521600c8ec"
down_revision: Union[str, None] = "9519290d3c95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TRIGGER update_user_role_bindings_updated_at_trigger
            BEFORE UPDATE ON user_role_bindings
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
        """
    )


def downgrade() -> None:
    op.execute(
        """
            DROP TRIGGER update_userg_role_bindings_updated_at_trigger
            ON userg_role_bindings;
        """
    )
