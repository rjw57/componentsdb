"""add_collections

Revision ID: ebb6ad8c9c40
Revises: 660d48ec93c5
Create Date: 2024-07-19 12:45:29.631086

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ebb6ad8c9c40"
down_revision: Union[str, None] = "660d48ec93c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "collections",
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("drawer_id", sa.BigInteger(), nullable=False),
        sa.Column("component_id", sa.BigInteger(), nullable=False),
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("uuid", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
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
        sa.CheckConstraint("count >= 0"),
        sa.ForeignKeyConstraint(
            ["component_id"],
            ["components.id"],
        ),
        sa.ForeignKeyConstraint(
            ["drawer_id"],
            ["drawers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_collections_uuid", "collections", ["uuid"], unique=False)
    # ### end Alembic commands ###
    op.execute(
        """
        CREATE TRIGGER update_collections_updated_at_trigger
            BEFORE UPDATE ON collections
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER update_collections_updated_at_trigger ON collections;")
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_collections_uuid", table_name="collections")
    op.drop_table("collections")
    # ### end Alembic commands ###
