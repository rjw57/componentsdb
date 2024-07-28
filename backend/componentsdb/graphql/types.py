from typing import Any, Optional

import strawberry
from strawberry.field_extensions import InputMutationExtension

from ..db import models as dbm
from . import context
from .pagination import Connection, Node, PaginationParams


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
class User(Node):
    db_resource: strawberry.Private[dbm.User]
    email: Optional[str]
    display_name: str
    avatar_url: Optional[str]


@strawberry.type
class Credentials:
    access_token: str
    refresh_token: str
    expires_in: int


@strawberry.type
class AuthQueries:
    @strawberry.field
    def federated_identity_providers(self) -> list[str]:
        raise NotImplementedError()

    @strawberry.field
    def me(self) -> Optional[User]:
        raise NotImplementedError()


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
class AuthMutations:
    @strawberry.mutation(extensions=[InputMutationExtension()])
    def signUpWithFederatedIdentity(
        self, info: strawberry.Info, provider: str, id_token: str
    ) -> User:
        raise NotImplementedError()

    @strawberry.mutation(extensions=[InputMutationExtension()])
    def signInWithFederatedIdentity(
        self, info: strawberry.Info, provider: str, id_token: str
    ) -> Credentials:
        raise NotImplementedError()

    @strawberry.mutation(extensions=[InputMutationExtension()])
    def refreshCredentials(self, info: strawberry.Info, refresh_token: str) -> Credentials:
        raise NotImplementedError()


@strawberry.type
class Mutation:
    @strawberry.field
    def auth(self) -> AuthMutations:
        return AuthMutations()
