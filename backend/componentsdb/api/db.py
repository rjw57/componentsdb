from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import models as dbm
from . import models as m

DEFAULT_LIMIT = 100


def select_starting_at_uuid(model: type[dbm.Base], uuid: UUID):
    subquery = (
        sa.select(model.id).where(model.uuid == uuid).order_by(model.id.asc()).scalar_subquery()
    )
    return sa.select(model).where(model.id >= subquery)


async def cabinets_list(
    session: AsyncSession, cursor: Optional[UUID] = None, limit: Optional[int] = None
) -> m.CabinetList:
    limit = limit if limit is not None else DEFAULT_LIMIT
    if cursor is None:
        stmt = sa.select(dbm.Cabinet)
    else:
        stmt = select_starting_at_uuid(dbm.Cabinet, cursor)

    stmt = stmt.limit(limit + 1).options(sa.orm.selectinload(dbm.Cabinet.drawers))

    cabinets = (await session.execute(stmt)).scalars().all()
    items = [
        m.CabinetSummary(
            id=str(c.uuid),
            name=c.name,
            drawers=[m.DrawerSummary(id=str(d.uuid), label=d.label) for d in c.drawers],
        )
        for c in cabinets[:limit]
    ]

    if len(cabinets) <= limit:
        next_cursor = None
    else:
        next_cursor = cabinets[-1].uuid

    return m.CabinetList(items=items[:limit], nextCursor=next_cursor)
