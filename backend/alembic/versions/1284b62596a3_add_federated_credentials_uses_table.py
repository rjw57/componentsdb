"""add_federated_credentials_uses_table

Revision ID: 1284b62596a3
Revises: 2730d92f2c4d
Create Date: 2024-07-29 07:55:17.976386

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1284b62596a3"
down_revision: Union[str, None] = "2730d92f2c4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "federated_user_credential_uses",
        sa.Column(
            "claims",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("json_build_object()"),
            nullable=False,
        ),
        sa.Column("id", sa.BigInteger(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_federated_user_credential_uses_claims",
        "federated_user_credential_uses",
        ["claims"],
        unique=False,
        postgresql_using="gin",
    )
    op.drop_column("federated_user_credentials", "most_recent_claims")
    # ### end Alembic commands ###
    op.execute(
        """
        CREATE TRIGGER update_federated_user_credential_uses_updated_at_trigger
            BEFORE UPDATE ON federated_user_credential_uses
            FOR EACH ROW EXECUTE PROCEDURE update_updated_at_col()
        ;
        """
    )


def downgrade() -> None:
    op.execute(
        """
            DROP TRIGGER update_federated_user_credential_uses_updated_at_trigger
            ON federated_user_credential_uses;
        """
    )
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "federated_user_credentials",
        sa.Column(
            "most_recent_claims",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("json_build_object()"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_index(
        "idx_federated_user_credential_uses_claims",
        table_name="federated_user_credential_uses",
        postgresql_using="gin",
    )
    op.drop_table("federated_user_credential_uses")
    # ### end Alembic commands ###
