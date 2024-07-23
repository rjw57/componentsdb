from typing import Optional

import strawberry

from ..db import models as dbm
from .pagination import Connection, Node, PaginationParams


@strawberry.type
class Cabinet(Node):
    db_resource: strawberry.Private[dbm.Cabinet]
    name: str

    @strawberry.field
    def drawers(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> "Connection[Drawer]":
        return info.context["db_loaders"]["cabinet_drawer_connection"].make_connection(
            self.db_resource.id, PaginationParams(after=after, first=first)
        )


@strawberry.type
class Drawer(Node):
    db_resource: strawberry.Private[dbm.Drawer]
    label: str

    @strawberry.field
    def collections(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> "Connection[Collection]":
        return info.context["db_loaders"]["drawer_collection_connection"].make_connection(
            self.db_resource.id, PaginationParams(after=after, first=first)
        )

    @strawberry.field
    async def cabinet(self, info: strawberry.Info) -> Cabinet:
        return await info.context["db_loaders"]["related_cabinet"].load(
            self.db_resource.cabinet_id
        )


@strawberry.type
class Collection(Node):
    db_resource: strawberry.Private[dbm.Collection]
    count: int

    @strawberry.field
    async def component(self, info: strawberry.Info) -> "Component":
        return await info.context["db_loaders"]["related_component"].load(
            self.db_resource.component_id
        )

    @strawberry.field
    async def drawer(self, info: strawberry.Info) -> "Drawer":
        return await info.context["db_loaders"]["related_drawer"].load(self.db_resource.drawer_id)


@strawberry.type
class Component(Node):
    db_resource: strawberry.Private[dbm.Component]
    code: str
    description: Optional[str]
    datasheet_url: Optional[str]

    @strawberry.field
    def collections(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> "Connection[Collection]":
        return info.context["db_loaders"]["component_collection_connection"].make_connection(
            self.db_resource.id, PaginationParams(after=after, first=first)
        )


@strawberry.type
class Query:
    @strawberry.field
    def cabinets(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> Connection[Cabinet]:
        return info.context["db_loaders"]["cabinet_connection"].make_connection(
            None, PaginationParams(after=after, first=first)
        )

    @strawberry.field
    async def cabinet(self, info: strawberry.Info, id: strawberry.ID) -> Cabinet:
        return await info.context["db_loaders"]["cabinet"].load(id)
