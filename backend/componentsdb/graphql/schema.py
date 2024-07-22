from typing import Any, Optional

import strawberry
from sqlalchemy.ext.asyncio import AsyncSession

from . import db
from .pagination import Connection, Node, PaginationParams


@strawberry.type
class Cabinet(Node):
    name: str

    @strawberry.field
    def drawers(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> Connection["Drawer", Any]:
        return info.context["db_loaders"]["cabinet_drawer_connection"].make_connection(
            self.db_id, PaginationParams(after=after, first=first)
        )


@strawberry.type
class Drawer(Node):
    label: str


@strawberry.type
class Query:
    @strawberry.field
    def cabinets(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> Connection[Cabinet, Any]:
        return info.context["db_loaders"]["cabinet_connection"].make_connection(
            None, PaginationParams(after=after, first=first)
        )


def context_from_db_session(session: AsyncSession):
    return {
        "db_loaders": {
            "cabinet_connection": db.CabinetConnectionLoader(session),
            "cabinet_drawer_connection": db.CabinetDrawerConnectionLoader(session),
        }
    }


schema = strawberry.Schema(query=Query)
