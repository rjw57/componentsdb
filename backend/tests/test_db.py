import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb import models


@pytest.mark.asyncio
async def test_db_connection(db_session: AsyncSession):
    "Database connection is valid."
    assert (1,) == (await db_session.execute(sa.select(1))).first()


@pytest.mark.asyncio
async def test_cabinets_table_exists(db_session: AsyncSession):
    await db_session.execute(sa.select(models.Cabinet))
