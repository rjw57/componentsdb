import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb.db import models as m


@pytest.mark.asyncio
async def test_cabinets_fixture(cabinets: list[m.Cabinet], db_session: AsyncSession):
    (n,) = (await db_session.execute(sa.select(sa.func.count("*")).select_from(m.Cabinet))).first()
    assert n == len(cabinets)


@pytest.mark.asyncio
async def test_components_fixture(components: list[m.Component], db_session: AsyncSession):
    (n,) = (
        await db_session.execute(sa.select(sa.func.count("*")).select_from(m.Component))
    ).first()
    assert n == len(components)


@pytest.mark.asyncio
async def test_drawers_fixture(drawers: list[m.Component], db_session: AsyncSession):
    (n,) = (await db_session.execute(sa.select(sa.func.count("*")).select_from(m.Drawer))).first()
    assert n == len(drawers)


@pytest.mark.asyncio
async def test_collections_fixture(collections: list[m.Component], db_session: AsyncSession):
    (n,) = (
        await db_session.execute(sa.select(sa.func.count("*")).select_from(m.Collection))
    ).first()
    assert n == len(collections)
