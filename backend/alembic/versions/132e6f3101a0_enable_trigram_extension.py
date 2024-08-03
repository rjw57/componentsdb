"""enable_trigram_extension

Revision ID: 132e6f3101a0
Revises: 1284b62596a3
Create Date: 2024-08-03 19:58:36.773173

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "132e6f3101a0"
down_revision: Union[str, None] = "1284b62596a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))


def downgrade() -> None:
    op.execute(sa.text("DROP EXTENSION IF EXISTS pg_trgm"))
