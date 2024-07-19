import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb.db import fakes as f
from componentsdb.db import models as m


@pytest_asyncio.fixture
async def cabinets(faker: Faker, db_session: AsyncSession):
    cabinets = [f.fake_cabinet(faker) for _ in range(40)]
    db_session.add_all(cabinets)
    await db_session.flush()
    return cabinets


@pytest_asyncio.fixture
async def components(faker: Faker, db_session: AsyncSession):
    components = [f.fake_component(faker) for _ in range(200)]
    db_session.add_all(components)
    await db_session.flush()
    return components


@pytest_asyncio.fixture
async def drawers(faker: Faker, cabinets: list[m.Cabinet], db_session: AsyncSession):
    drawers = [f.fake_drawer(faker, cabinet=faker.random_element(cabinets)) for _ in range(100)]
    db_session.add_all(drawers)
    await db_session.flush()
    return drawers


@pytest_asyncio.fixture
async def collections(
    faker: Faker, drawers: list[m.Drawer], components: list[m.Component], db_session: AsyncSession
):
    collections = [
        f.fake_collection(
            faker, drawer=faker.random_element(drawers), component=faker.random_element(components)
        )
        for _ in range(50)
    ]
    db_session.add_all(collections)
    await db_session.flush()
    return collections


@pytest_asyncio.fixture
async def all_fakes(collections, cabinets, drawers, components):
    pass
