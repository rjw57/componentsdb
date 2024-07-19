import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb.db import fakes as f


@pytest.mark.asyncio
async def test_cabinet(faker: Faker, db_session: AsyncSession):
    c = f.fake_cabinet(faker)
    db_session.add(c)
    await db_session.flush()
    assert c.id != 0


@pytest.mark.asyncio
async def test_component(faker: Faker, db_session: AsyncSession):
    c = f.fake_component(faker)
    db_session.add(c)
    await db_session.flush()
    assert c.id != 0


@pytest.mark.asyncio
async def test_drawer(faker: Faker, db_session: AsyncSession):
    d = f.fake_drawer(faker)
    db_session.add(d)
    await db_session.flush()
    assert d.id != 0
    assert d.cabinet is not None
    assert d.cabinet.uuid is not None


@pytest.mark.asyncio
async def test_drawer_with_cabinet(faker: Faker, db_session: AsyncSession):
    c = f.fake_cabinet(faker)
    d = f.fake_drawer(faker, cabinet=c)
    db_session.add_all([c, d])
    await db_session.flush()
    assert d.id != 0
    assert d.cabinet is not None
    assert d.cabinet.uuid == c.uuid
