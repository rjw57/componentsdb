import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb.db import models as m


async def assert_object_count(db_session, expected_count, model):
    (n,) = (await db_session.execute(sa.select(sa.func.count("*")).select_from(model))).first()
    assert n == expected_count


@pytest.mark.asyncio
async def test_cabinets_fixture(cabinets: list[m.Cabinet], db_session: AsyncSession):
    await assert_object_count(db_session, len(cabinets), m.Cabinet)


@pytest.mark.asyncio
async def test_components_fixture(components: list[m.Component], db_session: AsyncSession):
    await assert_object_count(db_session, len(components), m.Component)


@pytest.mark.asyncio
async def test_drawers_fixture(drawers: list[m.Drawer], db_session: AsyncSession):
    await assert_object_count(db_session, len(drawers), m.Drawer)


@pytest.mark.asyncio
async def test_collections_fixture(collections: list[m.Collection], db_session: AsyncSession):
    await assert_object_count(db_session, len(collections), m.Collection)
