from typing import Any, Optional

import strawberry

from ..db import models as dbm
from . import context
from .authtypes import AuthMutations, AuthQueries
from .paginationtypes import Connection, Node, PaginationParams


def _db(context_: dict[str, Any]) -> "context.DbContext":
    db = context_.get("db")
    if db is None or not isinstance(db, context.DbContext):
        raise ValueError("context has no DbContext instance available via the 'db' key")
    return db


@strawberry.type
class Cabinet(Node):
    db_resource: strawberry.Private[dbm.Cabinet]
    name: str

    @strawberry.field
    def drawers(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> "Connection[Drawer]":
        return _db(info.context).cabinet_drawer_connection.make_connection(
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
        return _db(info.context).drawer_collection_connection.make_connection(
            self.db_resource.id, PaginationParams(after=after, first=first)
        )

    @strawberry.field
    async def cabinet(self, info: strawberry.Info) -> Cabinet:
        return await _db(info.context).related_cabinet.load(self.db_resource.cabinet_id)


@strawberry.type
class Collection(Node):
    db_resource: strawberry.Private[dbm.Collection]
    count: int

    @strawberry.field
    async def component(self, info: strawberry.Info) -> "Component":
        return await _db(info.context).related_component.load(self.db_resource.component_id)

    @strawberry.field
    async def drawer(self, info: strawberry.Info) -> "Drawer":
        return await _db(info.context).related_drawer.load(self.db_resource.drawer_id)


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
        return _db(info.context).component_collection_connection.make_connection(
            self.db_resource.id, PaginationParams(after=after, first=first)
        )


@strawberry.type
class Query:
    @strawberry.field
    def auth(self) -> AuthQueries:
        return AuthQueries()

    @strawberry.field
    def cabinets(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> Connection[Cabinet]:
        return _db(info.context).cabinet_connection.make_connection(
            None, PaginationParams(after=after, first=first)
        )

    @strawberry.field
    async def cabinet(self, info: strawberry.Info, id: strawberry.ID) -> Optional[Cabinet]:
        return await _db(info.context).cabinet.load(id)


@strawberry.type
class Mutation:
    @strawberry.field
    def auth(self) -> AuthMutations:
        return AuthMutations()
