"""add_role_binding_tables

Revision ID: 9519290d3c95
Revises: 3c6509c01c97
Create Date: 2024-08-18 10:19:19.655862

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9519290d3c95"
down_revision: Union[str, None] = "3c6509c01c97"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_role_bindings",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role_id", sa.String(), nullable=False),
        sa.Column("target", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )
    op.create_index("idx_use_role_binding_target", "user_role_bindings", ["target"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_use_role_binding_target", table_name="user_role_bindings")
    op.drop_table("user_role_bindings")
    # ### end Alembic commands ###