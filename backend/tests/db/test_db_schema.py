import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql import text


@pytest_asyncio.fixture
async def fake_cabinet_id(db_engine: AsyncEngine, faker: Faker):
    async with db_engine.connect() as conn:
        name = faker.bs()
        id = (
            await conn.execute(
                text("INSERT INTO cabinets (name) VALUES (:name) RETURNING id"), {"name": name}
            )
        ).first()[0]
        await conn.commit()
    return id


@pytest.mark.asyncio
async def test_cabinets_uuid_default(db_engine: AsyncEngine, fake_cabinet_id):
    """uuid column is set on INSERT."""
    async with db_engine.connect() as conn:
        uuid = (
            await conn.execute(
                text("SELECT uuid FROM cabinets WHERE id = :id"), {"id": fake_cabinet_id}
            )
        ).first()[0]
        assert uuid is not None


@pytest.mark.asyncio
async def test_cabinets_at_fields_default(db_engine: AsyncEngine, fake_cabinet_id):
    """created_at and updated_at set on INSERT."""
    async with db_engine.connect() as conn:
        created_at, updated_at = (
            await conn.execute(
                text("SELECT created_at, updated_at FROM cabinets WHERE id = :id"),
                {"id": fake_cabinet_id},
            )
        ).first()
        assert created_at is not None
        assert updated_at is not None
        assert updated_at == created_at


@pytest.mark.asyncio
async def test_cabinets_updated_at_updated(faker: Faker, db_engine: AsyncEngine, fake_cabinet_id):
    """updated_at is updated when rows are updated."""
    async with db_engine.connect() as conn:
        await conn.execute(
            text("UPDATE cabinets SET name = :name WHERE id = :id"),
            {"id": fake_cabinet_id, "name": faker.bs()},
        )
        await conn.commit()

    async with db_engine.connect() as conn:
        created_at, updated_at = (
            await conn.execute(
                text("SELECT created_at, updated_at FROM cabinets WHERE id = :id"),
                {"id": fake_cabinet_id},
            )
        ).first()
        assert created_at is not None
        assert updated_at is not None
        assert updated_at > created_at
