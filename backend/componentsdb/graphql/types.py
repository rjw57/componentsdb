from typing import Optional

import strawberry

from .pagination import Connection, Node, PaginationParams


@strawberry.type
class Cabinet(Node):
    name: str

    @strawberry.field
    def drawers(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> "Connection[Drawer]":
        return info.context["db_loaders"]["cabinet_drawer_connection"].make_connection(
            self.db_id, PaginationParams(after=after, first=first)
        )


@strawberry.type
class Drawer(Node):
    label: str

    @strawberry.field
    def collections(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> "Connection[Collection]":
        return info.context["db_loaders"]["drawer_collection_connection"].make_connection(
            self.db_id, PaginationParams(after=after, first=first)
        )


@strawberry.type
class Collection(Node):
    count: int
