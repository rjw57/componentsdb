"""create_initial_tables_and_indexes

Revision ID: 9cce51e5ac43
Revises:
Create Date: 2024-07-18 11:56:19.799394

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9cce51e5ac43"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "cabinets",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "uuid", sa.UUID(), nullable=False, server_default=sa.Function("gen_random_uuid")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.Function("now"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.Function("now"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_cabinets_uuid", "cabinets", ["uuid"], unique=False)
    op.create_table(
        "components",
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("datasheet_url", sa.String(), nullable=True),
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "uuid", sa.UUID(), nullable=False, server_default=sa.Function("gen_random_uuid")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.Function("now"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.Function("now"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_components_uuid", "components", ["uuid"], unique=False)
    op.create_table(
        "drawers",
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("cabinet_id", sa.BigInteger(), nullable=False),
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "uuid", sa.UUID(), nullable=False, server_default=sa.Function("gen_random_uuid")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.Function("now"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.Function("now"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["cabinet_id"],
            ["cabinets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_drawers_uuid", "drawers", ["uuid"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_drawers_uuid", table_name="drawers")
    op.drop_table("drawers")
    op.drop_index("idx_components_uuid", table_name="components")
    op.drop_table("components")
    op.drop_index("idx_cabinets_uuid", table_name="cabinets")
    op.drop_table("cabinets")
    # ### end Alembic commands ###