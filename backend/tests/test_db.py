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


@pytest.mark.asyncio
async def test_cabinets_auto_fields(db_session: AsyncSession):
    cabinet = models.Cabinet(name="testing-name")
    db_session.add(cabinet)
    await db_session.flush()
    assert cabinet.id != 0
    assert cabinet.uuid is not None
    assert cabinet.created_at is not None
    assert cabinet.updated_at is not None
