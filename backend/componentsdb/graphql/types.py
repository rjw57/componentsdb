from typing import NamedTuple, Optional

import strawberry

from ..db import models as dbm
from . import context
from .authtypes import AuthMutations, AuthQueries
from .paginationtypes import Connection, Node, PaginationParams
from .rbactypes import RBACQueries


@strawberry.type
class Cabinet(Node):
    db_resource: strawberry.Private[dbm.Cabinet]
    name: str

    @strawberry.field
    def drawers(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> "Connection[Drawer]":
        return context.get_db(info.context).cabinet_drawer_connection.make_connection(
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
        return context.get_db(info.context).drawer_collection_connection.make_connection(
            self.db_resource.id, PaginationParams(after=after, first=first)
        )

    @strawberry.field
    async def cabinet(self, info: strawberry.Info) -> Cabinet:
        return await context.get_db(info.context).related_cabinet.load(self.db_resource.cabinet_id)


@strawberry.type
class Collection(Node):
    db_resource: strawberry.Private[dbm.Collection]
    count: int

    @strawberry.field
    async def component(self, info: strawberry.Info) -> "Component":
        return await context.get_db(info.context).related_component.load(
            self.db_resource.component_id
        )

    @strawberry.field
    async def drawer(self, info: strawberry.Info) -> "Drawer":
        return await context.get_db(info.context).related_drawer.load(self.db_resource.drawer_id)


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
        return context.get_db(info.context).component_collection_connection.make_connection(
            self.db_resource.id, PaginationParams(after=after, first=first)
        )


class ComponentQueryKey(NamedTuple):
    search: Optional[str] = None


@strawberry.type
class Query:
    @strawberry.field
    def auth(self) -> AuthQueries:
        return AuthQueries()

    @strawberry.field
    def rbac(self) -> RBACQueries:
        return RBACQueries()

    @strawberry.field
    def cabinets(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> Connection[Cabinet]:
        return context.get_db(info.context).cabinet_connection.make_connection(
            None, PaginationParams(after=after, first=first)
        )

    @strawberry.field
    async def cabinet(self, info: strawberry.Info, id: strawberry.ID) -> Optional[Cabinet]:
        return await context.get_db(info.context).cabinet.load(id)

    @strawberry.field
    def components(
        self,
        info: strawberry.Info,
        search: Optional[str] = None,
        after: Optional[str] = None,
        first: Optional[int] = None,
    ) -> Connection[Component]:
        return context.get_db(info.context).component_connection.make_connection(
            ComponentQueryKey(search=search), PaginationParams(after=after, first=first)
        )


@strawberry.type
class Mutation:
    @strawberry.field
    def auth(self) -> AuthMutations:
        return AuthMutations()
