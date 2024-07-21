import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlalchemy.sql import text

from componentsdb.db import fakes as f

RESOURCE_TABLES = ["cabinets", "drawers", "collections", "components"]


@pytest_asyncio.fixture
async def fake_items(db_engine: AsyncEngine, faker: Faker):
    session = async_sessionmaker(db_engine, expire_on_commit=False)()
    async with session.begin():
        session.add(f.fake_cabinet(faker))
        session.add(f.fake_drawer(faker))
        session.add(f.fake_component(faker))
        session.add(f.fake_collection(faker))
        await session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize("table", RESOURCE_TABLES)
async def test_resource_uuid_default(table: str, db_engine: AsyncEngine, fake_items):
    """uuid column is set on INSERT."""
    async with db_engine.connect() as conn:
        uuid = (await conn.execute(text(f"SELECT uuid FROM {table} ORDER BY id ASC"))).scalar()
        assert uuid is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("table", RESOURCE_TABLES)
async def test_resource_at_fields_default(table: str, db_engine: AsyncEngine, fake_items):
    """created_at and updated_at set on INSERT."""
    async with db_engine.connect() as conn:
        created_at, updated_at = (
            await conn.execute(
                text(f"SELECT created_at, updated_at FROM {table} ORDER BY id ASC LIMIT 1")
            )
        ).one()
        assert created_at is not None
        assert updated_at is not None
        assert updated_at == created_at


@pytest.mark.asyncio
@pytest.mark.parametrize("table", RESOURCE_TABLES)
async def test_updated_at_updated(table: str, fake_items, faker: Faker, db_engine: AsyncEngine):
    """updated_at is updated when rows are updated."""
    async with db_engine.connect() as conn:
        id = (await conn.execute(text(f"SELECT id FROM {table} ORDER BY id"))).scalar()
        match table:
            case "cabinets":
                await conn.execute(
                    text("UPDATE cabinets SET name = :name WHERE id = :id"),
                    {"id": id, "name": faker.bs()},
                )
            case "drawers":
                await conn.execute(
                    text("UPDATE drawers SET label = :label WHERE id = :id"),
                    {"id": id, "label": faker.bs()},
                )
            case "components":
                await conn.execute(
                    text("UPDATE components SET code = :code WHERE id = :id"),
                    {"id": id, "code": faker.bs()},
                )
            case "collections":
                await conn.execute(
                    text(
                        """
                        UPDATE collections
                        SET
                            component_id = (SELECT id FROM components ORDER BY id LIMIT 1),
                            drawer_id = (SELECT id FROM drawers ORDER BY id LIMIT 1)
                        WHERE id = :id
                        """
                    ),
                    {"id": id, "code": faker.bs()},
                )
            case _:
                raise NotImplementedError()
        await conn.commit()

    async with db_engine.connect() as conn:
        created_at, updated_at = (
            await conn.execute(
                text(f"SELECT created_at, updated_at FROM {table} WHERE id = :id"),
                {"id": id},
            )
        ).one()
        assert created_at is not None
        assert updated_at is not None
        assert updated_at > created_at
