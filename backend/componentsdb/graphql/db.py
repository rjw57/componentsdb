import base64
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import models as dbm
from . import schema as s

DEFAULT_LIMIT = 100


def select_after_uuid(model: type[dbm.Base], uuid: UUID):
    subquery = (
        sa.select(model.id).where(model.uuid == uuid).order_by(model.id.asc()).scalar_subquery()
    )
    return sa.select(model).where(model.id > subquery)


def uuid_from_cursor(cursor: str) -> UUID:
    return UUID(bytes=base64.b64decode(cursor))


def cursor_from_uuid(uuid_: UUID) -> str:
    return base64.standard_b64encode(uuid_.bytes).decode("ascii")


async def query_cabinets(
    session: AsyncSession, after: Optional[str] = None, limit: Optional[int] = None
) -> "s.Connection[s.Cabinet]":
    limit = limit if limit is not None else DEFAULT_LIMIT
    if after is None:
        stmt = sa.select(dbm.Cabinet).order_by(dbm.Cabinet.id)
    else:
        stmt = select_after_uuid(dbm.Cabinet, uuid_from_cursor(after))
    stmt = stmt.limit(limit + 1)
    cabinets = (await session.execute(stmt)).scalars().all()
    return _cabinet_connection(cabinets, limit)


async def count_cabinets(session: AsyncSession) -> int:
    return (await session.execute(sa.Select(sa.func.count(dbm.Cabinet.id)))).scalar()


async def query_drawers_for_cabinet_ids(
    db_session: AsyncSession, cabinet_uuids: list[str | UUID], limit: Optional[int] = None
) -> list["s.Connection[s.Drawer]"]:
    limit = limit if limit is not None else DEFAULT_LIMIT
    subq = (
        sa.select(dbm.Drawer)
        .where(dbm.Drawer.cabinet_id == dbm.Cabinet.id)
        .order_by(dbm.Drawer.id.asc())
        .limit(limit + 1)
        .subquery()
        .lateral()
        .alias("drawers")
    )
    stmt = (
        sa.select(dbm.Cabinet)
        .outerjoin(subq)
        .where(dbm.Cabinet.uuid.in_(cabinet_uuids))
        .options(
            sa.orm.load_only(dbm.Cabinet.id),
            sa.orm.contains_eager(dbm.Cabinet.drawers, alias=subq),
        )
    )
    cabinets_by_uuid = {
        str(c.uuid): c for c in (await db_session.execute(stmt)).unique().scalars()
    }
    return [
        _drawer_connection(c.drawers if c is not None else [], limit)
        for c in (cabinets_by_uuid.get(str(id_)) for id_ in cabinet_uuids)
    ]


def _cabinet_connection(cabinets: list[dbm.Cabinet], limit: int) -> "s.Connection[s.Cabinet]":
    edges = [
        s.Edge(
            cursor=cursor_from_uuid(c.uuid),
            node=s.Cabinet(
                id=c.uuid,
                name=c.name,
            ),
        )
        for c in cabinets[:limit]
    ]

    page_info = s.PageInfo(
        end_cursor=cursor_from_uuid(cabinets[limit - 1].uuid) if len(cabinets) > limit else None,
        has_next_page=len(cabinets) > limit,
    )

    return s.Connection(edges=edges, page_info=page_info)


def _drawer_connection(drawers: list[dbm.Drawer], limit: int) -> "s.Connection[s.Drawer]":
    edges = [
        s.Edge(
            cursor=cursor_from_uuid(c.uuid),
            node=s.Drawer(
                id=c.uuid,
                label=c.label,
            ),
        )
        for c in drawers[:limit]
    ]

    page_info = s.PageInfo(
        end_cursor=cursor_from_uuid(drawers[limit - 1].uuid) if len(drawers) > limit else None,
        has_next_page=len(drawers) > limit,
    )

    return s.Connection(edges=edges, page_info=page_info)
