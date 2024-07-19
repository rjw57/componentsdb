import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb.api import db
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


@pytest.mark.asyncio
@pytest.mark.parametrize("model", [m.Cabinet, m.Drawer, m.Collection, m.Component])
async def test_select_after_uuid(model: m.Base, db_session: AsyncSession, all_fakes):
    all_items = (
        (await db_session.execute(sa.select(model).order_by(model.id.asc()))).scalars().all()
    )
    pivot_idx = len(all_items) >> 1
    assert pivot_idx > 0
    pivot = all_items[pivot_idx]
    after_items = (
        (await db_session.execute(db.select_starting_at_uuid(model, pivot.uuid))).scalars().all()
    )
    assert len(after_items) == len(all_items) - pivot_idx
    for item in after_items:
        assert item.id >= pivot.id


@pytest.mark.asyncio
@pytest.mark.parametrize("model", [m.Cabinet, m.Drawer, m.Collection, m.Component])
async def test_select_after_uuid_no_match(model: m.Base, db_session: AsyncSession, all_fakes):
    all_items = (
        (await db_session.execute(sa.select(model).order_by(model.id.asc()))).scalars().all()
    )
    assert len(all_items) > 0
    after_uuid = uuid.uuid4()
    after_items = (
        (await db_session.execute(db.select_starting_at_uuid(model, after_uuid))).scalars().all()
    )
    assert len(after_items) == 0
