import uuid

import pytest
import sqlalchemy as sa
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from componentsdb.api import db
from componentsdb.api import models as apim
from componentsdb.db import fakes as f
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


def assert_cabinets_match_summaries(
    expected: list[m.Cabinet], summaries: list[apim.CabinetSummary]
):
    assert len(expected) == len(summaries)
    for e, s in zip(expected, summaries):
        assert e.uuid == s.id
        assert e.name == s.name


def assert_drawers_match_summaries(expected: list[m.Drawer], summaries: list[apim.DrawerSummary]):
    assert len(expected) == len(summaries)
    for e, s in zip(expected, summaries):
        assert e.uuid == s.id
        assert e.label == s.label


@pytest.mark.asyncio
async def test_cabinet_list(
    faker: Faker, db_session: AsyncSession, cabinets: list[m.Cabinet], all_fakes
):
    # Sort cabinets by id
    cabinets = sorted(cabinets, key=lambda c: c.id)

    # Ensure first cabinet has some drawers
    db_session.add_all([f.fake_drawer(faker, cabinet=cabinets[0]) for _ in range(10)])
    await db_session.flush()

    assert len(cabinets) > 30
    resp = await db.cabinets_list(db_session, None, 10)
    expected = cabinets[:10]
    assert_cabinets_match_summaries(expected, resp.items)
    assert len(resp.items[0].drawers) > 0
    assert resp.next_cursor is not None
    resp = await db.cabinets_list(db_session, resp.next_cursor, 10)
    expected = cabinets[10:20]
    assert_cabinets_match_summaries(expected, resp.items)
    resp = await db.cabinets_list(db_session, cabinets[-2].uuid, 10)
    expected = cabinets[-2:]
    assert_cabinets_match_summaries(expected, resp.items)
    resp = await db.cabinets_list(db_session, uuid.uuid4(), 10)
    assert len(resp.items) == 0
