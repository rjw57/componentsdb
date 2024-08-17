import asyncio
from functools import cache
from typing import Any, Callable, Optional, TypeVar

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import AuthenticationProvider
from ..db import models as dbm
from . import rbactypes, types
from .genericloaders import (
    EntityConnectionFactory,
    EntityLoader,
    OneToManyRelationshipConnectionFactory,
    RelatedEntityLoader,
)


def cabinet_node_factory(o: dbm.Cabinet) -> "types.Cabinet":
    return types.Cabinet(db_resource=o, id=o.uuid, name=o.name)


def drawer_node_factory(o: dbm.Drawer) -> "types.Drawer":
    return types.Drawer(db_resource=o, id=o.uuid, label=o.label)


def collection_node_factory(o: dbm.Collection) -> "types.Collection":
    return types.Collection(db_resource=o, id=o.uuid, count=o.count)


def component_node_factory(o: dbm.Component) -> "types.Component":
    return types.Component(
        db_resource=o,
        id=o.uuid,
        code=o.code,
        description=o.description,
        datasheet_url=o.datasheet_url,
    )


def permission_node_factory(o: dbm.Permission) -> "rbactypes.Permission":
    return rbactypes.Permission(db_resource=o, id=o.id)


def role_node_factory(o: dbm.Role) -> "rbactypes.Role":
    return rbactypes.Role(db_resource=o, id=o.id)


class ComponentConnectionFactory(
    EntityConnectionFactory[dbm.Component, "types.Component", "types.ComponentQueryKey"]
):
    def __init__(self, session: AsyncSession, session_lock: asyncio.Lock):
        super().__init__(session, session_lock, dbm.Component, component_node_factory)

    def _similarity(self, key: "types.ComponentQueryKey"):
        return sa.func.word_similarity(sa.func.lower(key.search), dbm.Component.search_text)

    def ordering_keys(self, keys):
        return [-self._similarity(k) if k.search is not None else dbm.Component.id for k in keys]

    def filter(self, keys, stmt):
        threshold = 0.3
        return [
            (
                stmt.where(
                    self._similarity(k) > threshold,
                )
                if k.search is not None
                else stmt
            )
            for k in keys
        ]


_R = TypeVar("_R", bound=dbm.ResourceMixin)
_N = TypeVar("_N", bound="types.Node")
_K = TypeVar("_K")


class DbContext:
    db_session: AsyncSession
    db_lock: asyncio.Lock

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.db_lock = asyncio.Lock()

    def _make_entity_loader(
        self, mapper: Any, node_factory: Callable[[_R], _N]
    ) -> EntityLoader[_R, _N]:
        return EntityLoader[_R, _N](self.db_session, self.db_lock, mapper, node_factory)

    def _make_related_entity_loader(
        self, mapper: Any, node_factory: Callable[[_R], _N]
    ) -> RelatedEntityLoader[_R, _N]:
        return RelatedEntityLoader[_R, _N](self.db_session, self.db_lock, mapper, node_factory)

    def _make_entity_connection_factory(
        self, mapper: Any, node_factory: Callable[[_R], _N]
    ) -> EntityConnectionFactory[_R, _N, _K]:
        return EntityConnectionFactory[_R, _N, _K](
            self.db_session, self.db_lock, mapper, node_factory
        )

    def _make_one_to_many_relationship_connection_factory(
        self, relationship: Any, node_factory: Callable[[_R], _N]
    ) -> OneToManyRelationshipConnectionFactory[_R, _N]:
        return OneToManyRelationshipConnectionFactory[_R, _N](
            self.db_session, self.db_lock, relationship, node_factory
        )

    @cache
    def cabinet(self) -> EntityLoader[dbm.Cabinet, "types.Cabinet"]:
        return self._make_entity_loader(dbm.Cabinet, cabinet_node_factory)

    @cache
    def related_cabinet(self) -> RelatedEntityLoader[dbm.Cabinet, "types.Cabinet"]:
        return self._make_related_entity_loader(dbm.Cabinet, cabinet_node_factory)

    @cache
    def related_drawer(self) -> RelatedEntityLoader[dbm.Drawer, "types.Drawer"]:
        return self._make_related_entity_loader(dbm.Drawer, drawer_node_factory)

    @cache
    def related_component(self) -> RelatedEntityLoader[dbm.Component, "types.Component"]:
        return self._make_related_entity_loader(dbm.Component, component_node_factory)

    @cache
    def cabinet_connection(self) -> EntityConnectionFactory[dbm.Cabinet, "types.Cabinet", None]:
        return self._make_entity_connection_factory(dbm.Cabinet, cabinet_node_factory)

    @cache
    def cabinet_drawer_connection(
        self,
    ) -> OneToManyRelationshipConnectionFactory[dbm.Drawer, "types.Drawer"]:
        return self._make_one_to_many_relationship_connection_factory(
            dbm.Cabinet.drawers, drawer_node_factory
        )

    @cache
    def drawer_collection_connection(
        self,
    ) -> OneToManyRelationshipConnectionFactory[dbm.Collection, "types.Collection"]:
        return self._make_one_to_many_relationship_connection_factory(
            dbm.Drawer.collections, collection_node_factory
        )

    @cache
    def component_collection_connection(
        self,
    ) -> OneToManyRelationshipConnectionFactory[dbm.Collection, "types.Collection"]:
        return self._make_one_to_many_relationship_connection_factory(
            dbm.Component.collections, collection_node_factory
        )

    @cache
    def component_connection(self) -> ComponentConnectionFactory:
        return ComponentConnectionFactory(self.db_session, self.db_lock)

    @cache
    def permission_connection(
        self,
    ) -> EntityConnectionFactory[dbm.Permission, "rbactypes.Permission", None]:
        return self._make_entity_connection_factory(dbm.Permission, permission_node_factory)

    @cache
    def role_connection(self) -> EntityConnectionFactory[dbm.Role, "rbactypes.Role", None]:
        return self._make_entity_connection_factory(dbm.Role, role_node_factory)


def make_context(
    db_session: AsyncSession,
    authentication_provider: AuthenticationProvider,
    authenticated_user: Optional[dbm.User],
):
    return {
        "db": DbContext(db_session),
        "authentication_provider": authentication_provider,
        "authenticated_user": authenticated_user,
    }


def get_db(context_: dict[str, Any]) -> DbContext:
    db = context_.get("db")
    if db is None or not isinstance(db, DbContext):
        raise ValueError("context has no DbContext instance available via the 'db' key")
    return db
