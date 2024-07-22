from typing import Optional

import sqlalchemy as sa
import strawberry

from ..db import models as dbm
from . import loaders, types
from .pagination import PaginationParams


@strawberry.type
class Query:
    @strawberry.field
    def cabinets(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> types.CabinetConnection:
        return info.context["db_loaders"]["cabinet_connection"].make_connection(
            None, PaginationParams(after=after, first=first)
        )

    @strawberry.field
    async def cabinet(self, info: strawberry.Info, id: strawberry.ID) -> types.Cabinet:
        stmt = sa.select(dbm.Cabinet).where(dbm.Cabinet.uuid == id)
        cabinet = (await info.context["db_loaders"]["session"].execute(stmt)).scalar_one()
        return loaders.cabinet_node_from_db_model(cabinet)
