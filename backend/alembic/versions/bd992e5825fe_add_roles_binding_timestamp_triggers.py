"""add_roles_binding_timestamp_triggers

Revision ID: bd992e5825fe
Revises: 99a341f6afb5
Create Date: 2024-08-17 15:00:35.987277

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bd992e5825fe"
down_revision: Union[str, None] = "99a341f6afb5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TRIGGER update_user_global_role_bindings_updated_at_trigger
            BEFORE UPDATE ON user_global_role_bindings
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_user_cabinet_role_bindings_updated_at_trigger
            BEFORE UPDATE ON user_cabinet_role_bindings
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
        """
    )


def downgrade() -> None:
    op.execute(
        """
            DROP TRIGGER update_user_global_role_bindings_updated_at_trigger
            ON user_global_role_bindings;
        """
    )
    op.execute(
        """
            DROP TRIGGER update_user_cabinet_role_bindings_updated_at_trigger
            ON user_cabinet_role_bindings;
        """
    )
