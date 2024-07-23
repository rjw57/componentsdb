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


class CabinetLoader(EntityLoader[dbm.Cabinet, "types.Cabinet"]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, dbm.Cabinet, cabinet_node_factory)


class RelatedCabinetLoader(RelatedEntityLoader[dbm.Cabinet, "types.Cabinet"]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, dbm.Cabinet, cabinet_node_factory)


class CabinetConnectionFactory(EntityConnectionFactory[dbm.Cabinet, "types.Cabinet"]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, dbm.Cabinet, cabinet_node_factory)


class CabinetDrawerConnectionFactory(
    OneToManyRelationshipConnectionFactory[dbm.Drawer, "types.Drawer"]
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, dbm.Cabinet.drawers, drawer_node_factory)


class DrawerCollectionConnectionFactory(
    OneToManyRelationshipConnectionFactory[dbm.Collection, "types.Collection"]
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, dbm.Drawer.collections, collection_node_factory)
