"""add_refresh_token_and_expires_at_index_to_tokens

Revision ID: 2730d92f2c4d
Revises: 00aaee2ef63c
Create Date: 2024-07-28 13:47:37.359709

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2730d92f2c4d"
down_revision: Union[str, None] = "00aaee2ef63c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "refresh_tokens",
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
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
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("token"),
    )
    op.create_index(
        "idx_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"], unique=False
    )
    op.create_index("idx_access_tokens_expires_at", "access_tokens", ["expires_at"], unique=False)
    # ### end Alembic commands ###
    op.execute(
        """
        CREATE TRIGGER update_refresh_tokens_updated_at_trigger
            BEFORE UPDATE ON refresh_tokens
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER update_refresh_tokens_updated_at_trigger ON refresh_tokens;")
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_access_tokens_expires_at", table_name="access_tokens")
    op.drop_index("idx_refresh_tokens_expires_at", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    # ### end Alembic commands ###
