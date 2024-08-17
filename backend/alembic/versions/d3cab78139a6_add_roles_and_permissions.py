"""add_roles_and_permissions

Revision ID: d3cab78139a6
Revises: bd992e5825fe
Create Date: 2024-08-17 15:06:35.509048

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d3cab78139a6"
down_revision: Union[str, None] = "bd992e5825fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_ROLES = ["role/cabinetOwner", "role/cabinetViewer"]
NEW_PERMISSIONS = ["cabinet.read", "cabinet.write"]
NEW_ROLE_PERMISSION_BINDINGS = {
    "role/cabinetOwner": ["cabinet.read", "cabinet.write"],
    "role/cabinetViewer": ["cabinet.read"],
}


roles_table = sa.sql.table("roles", sa.sql.column("name", sa.String))
permissions_table = sa.sql.table("permissions", sa.sql.column("name", sa.String))
role_permission_bindings_table = sa.sql.table(
    "role_permission_bindings",
    sa.sql.column("role_name", sa.String),
    sa.sql.column("permission_name", sa.String),
)


def upgrade() -> None:
    op.bulk_insert(roles_table, [{"name": name} for name in NEW_ROLES])
    op.bulk_insert(permissions_table, [{"name": name} for name in NEW_PERMISSIONS])
    op.bulk_insert(
        role_permission_bindings_table,
        [
            {"role_name": role_name, "permission_name": permission_name}
            for role_name, permission_names in NEW_ROLE_PERMISSION_BINDINGS.items()
            for permission_name in permission_names
        ],
    )


def downgrade() -> None:
    for role_name, permissions in NEW_ROLE_PERMISSION_BINDINGS.items():
        op.execute(
            sa.delete(role_permission_bindings_table).where(
                role_permission_bindings_table.c.role_name == role_name,
                role_permission_bindings_table.c.permission_name.in_(permissions),
            )
        )
    op.execute(sa.delete(permissions_table).where(permissions_table.c.name.in_(NEW_PERMISSIONS)))
    op.execute(sa.delete(roles_table).where(roles_table.c.name.in_(NEW_ROLES)))
