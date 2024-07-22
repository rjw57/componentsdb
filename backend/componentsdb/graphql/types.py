from typing import Any, Optional

import strawberry

from .pagination import Connection, Node, PaginationParams


@strawberry.type
class Cabinet(Node):
    name: str

    @strawberry.field
    def drawers(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> "DrawerConnection":
        return info.context["db_loaders"]["cabinet_drawer_connection"].make_connection(
            self.db_id, PaginationParams(after=after, first=first)
        )


@strawberry.type
class CabinetConnection(Connection[Cabinet, Any]):
    pass


@strawberry.type
class Drawer(Node):
    label: str


@strawberry.type
class DrawerConnection(Connection[Drawer, Any]):
    pass
