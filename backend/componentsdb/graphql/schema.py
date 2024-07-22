from typing import Generic, Optional, TypeVar

import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from . import db


@strawberry.type
class PageInfo:
    end_cursor: Optional[str]
    has_next_page: bool


@strawberry.type
class Node:
    id: strawberry.ID


NodeType = TypeVar("NodeType", bound=Node)


@strawberry.type
class Edge(Generic[NodeType]):
    cursor: str
    node: NodeType


@strawberry.type
class Connection(Generic[NodeType]):
    edges: list[Edge[NodeType]]

    @strawberry.field
    async def nodes(self) -> list[NodeType]:
        return [e.node for e in self.edges]

    page_info: PageInfo


@strawberry.type
class Cabinet(Node):
    name: str

    @strawberry.field
    async def drawers(self, info: strawberry.Info) -> "Connection[Drawer]":
        return await info.context["loaders"]["drawers_for_cabinets"].load(self.id)


@strawberry.type
class Drawer(Node):
    label: str


@strawberry.type
class Query:
    @strawberry.field
    async def cabinets(
        self, info: strawberry.Info, after: Optional[str] = None, limit: Optional[int] = None
    ) -> Connection[Cabinet]:
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
