from typing import Optional

import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from . import db


@strawberry.type
class PageInfo:
    end_cursor: Optional[str]
    has_next_page: bool


@strawberry.type
class Cabinet:
    id: str
    name: str

    @strawberry.field
    async def drawers(self, info: strawberry.Info) -> "DrawerConnection":
        return await info.context["loaders"]["drawers_for_cabinets"].load(self.id)


@strawberry.type
class CabinetEdge:
    cursor: str
    node: Cabinet


@strawberry.type
class CabinetConnection:
    @strawberry.field
    async def count(self, info: strawberry.Info) -> int:
        return await db.count_cabinets(info.context["db_session"])

    edges: list[CabinetEdge]

    @strawberry.field
    async def nodes(self) -> list[Cabinet]:
        return [e.node for e in self.edges]

    page_info: PageInfo


@strawberry.type
class Drawer:
    id: str
    label: str


@strawberry.type
class DrawerEdge:
    cursor: str
    node: Drawer


@strawberry.type
class DrawerConnection:
    edges: list[DrawerEdge]

    @strawberry.field
    async def nodes(self) -> list[Drawer]:
        return [e.node for e in self.edges]

    page_info: PageInfo


@strawberry.type
class Query:
    @strawberry.field
    async def cabinets(
        self, info: strawberry.Info, after: Optional[str] = None, limit: Optional[int] = None
    ) -> CabinetConnection:
        db_session = info.context["db_session"]
        return await db.query_cabinets(db_session, after, limit)


def context_from_db_session(session: AsyncSession):
    return {
        "db_session": session,
        "loaders": {
            "drawers_for_cabinets": DataLoader(
                load_fn=lambda keys: db.query_drawers_for_cabinet_ids(session, keys)
            ),
        },
    }


schema = strawberry.Schema(query=Query)
