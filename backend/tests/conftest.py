import os

import pytest
import pytest_asyncio
from pytest_docker_tools import container
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import alembic.command
import alembic.config

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
                "postgresql://pytest-user@localhost:5432pytest-pass@/pytest-db?sslmode=disable",
            ],
            "interval": int(1e9),
            "timeout": int(3e9),
            "retries": 5,
            "start_period": int(120e9),
        },
        ports={
            "5432/tcp": None,
        },
    )

    @pytest.fixture(scope="session")
    def db_url(postgres_container):
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
    config.set_main_option("script_location", "alembic")
    config.set_main_option("sqlalchemy.url", db_url)
    return config


@pytest.fixture(scope="session")
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
