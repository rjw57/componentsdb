import os
import time

import pytest
import pytest_asyncio
from faker import Faker
from pytest_docker_tools import container
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import alembic.command
import alembic.config
from componentsdb.db import fakes as f
from componentsdb.db import models as m

_testing_db_url = os.environ.get("TESTING_DB_URL", "")

# We only spin up a dedicated database for the  test suite if TESTING_DB_URL is not set to
# a non-empty value.
if _testing_db_url == "":
    postgres_container = container(
        scope="session",
        image="postgres:16",
        environment={
            "POSTGRES_USER": "pytest-user",
            "POSTGRES_PASSWORD": "pytest-pass",
            "POSTGRES_DB": "pytest-db",
        },
        healthcheck={
            "test": [
                "CMD",
                "pg_isready",
                "--dbname",
                "postgresql://pytest-user:pytest-pass@localhost:5432/pytest-db?sslmode=disable",
            ],
            "interval": int(1e9),
            "timeout": int(3e9),
            "retries": 5,
            "start_period": int(120e9),
        },
        remove=True,
        ports={
            "5432/tcp": None,
        },
    )

    @pytest.fixture(scope="session")
    def db_url(postgres_container):
        # Wait for container to be healthy
        for _ in range(200):
            if postgres_container.attrs["State"]["Health"]["Status"] == "healthy":
                break
            time.sleep(0.2)
            postgres_container.reload()
        else:
            raise RuntimeError("Timed out waiting for container to be healthy")

        host, port = postgres_container.get_addr("5432/tcp")
        url = f"postgresql+asyncpg://pytest-user:pytest-pass@{host}:{port}/pytest-db"
        return url

else:

    @pytest.fixture(scope="session")
    def db_url():
        return _testing_db_url


@pytest.fixture(scope="session")
def alembic_config(db_url):
    config = alembic.config.Config()
    config.set_main_option(
        "script_location", os.path.join(os.path.dirname(__file__), "../", "alembic")
    )
    config.set_main_option("sqlalchemy.url", db_url)
    return config


@pytest.fixture
def migrated_db(alembic_config: alembic.config.Config):
    alembic.command.upgrade(alembic_config, "head")
    yield
    alembic.command.downgrade(alembic_config, "base")


@pytest_asyncio.fixture
async def db_engine(db_url, migrated_db):
    engine = create_async_engine(db_url, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    session = async_sessionmaker(db_engine, expire_on_commit=False)()
    print("Creating test transaction...")
    async with session.begin():
        yield session
        print("Rolling back test transaction...")
        await session.rollback()


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
