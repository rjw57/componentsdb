import asyncio

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import models as dbm
from . import types
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


class CabinetLoader(EntityLoader[dbm.Cabinet, "types.Cabinet"]):
    def __init__(self, session: AsyncSession, session_lock: asyncio.Lock):
        super().__init__(session, session_lock, dbm.Cabinet, cabinet_node_factory)


class RelatedCabinetLoader(RelatedEntityLoader[dbm.Cabinet, "types.Cabinet"]):
    def __init__(self, session: AsyncSession, session_lock: asyncio.Lock):
        super().__init__(session, session_lock, dbm.Cabinet, cabinet_node_factory)


class RelatedDrawerLoader(RelatedEntityLoader[dbm.Drawer, "types.Drawer"]):
    def __init__(self, session: AsyncSession, session_lock: asyncio.Lock):
        super().__init__(session, session_lock, dbm.Drawer, drawer_node_factory)


class RelatedComponentLoader(RelatedEntityLoader[dbm.Component, "types.Component"]):
    def __init__(self, session: AsyncSession, session_lock: asyncio.Lock):
        super().__init__(session, session_lock, dbm.Component, component_node_factory)


class CabinetConnectionFactory(EntityConnectionFactory[dbm.Cabinet, "types.Cabinet", None]):
    def __init__(self, session: AsyncSession, session_lock: asyncio.Lock):
        super().__init__(session, session_lock, dbm.Cabinet, cabinet_node_factory)


class CabinetDrawerConnectionFactory(
    OneToManyRelationshipConnectionFactory[dbm.Drawer, "types.Drawer"]
):
    def __init__(self, session: AsyncSession, session_lock: asyncio.Lock):
        super().__init__(session, session_lock, dbm.Cabinet.drawers, drawer_node_factory)


class DrawerCollectionConnectionFactory(
    OneToManyRelationshipConnectionFactory[dbm.Collection, "types.Collection"]
):
    def __init__(self, session: AsyncSession, session_lock: asyncio.Lock):
        super().__init__(session, session_lock, dbm.Drawer.collections, collection_node_factory)


class ComponentCollectionConnectionFactory(
    OneToManyRelationshipConnectionFactory[dbm.Collection, "types.Collection"]
):
    def __init__(self, session: AsyncSession, session_lock: asyncio.Lock):
        super().__init__(session, session_lock, dbm.Component.collections, collection_node_factory)


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
