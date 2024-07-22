from sqlalchemy.ext.asyncio import AsyncSession

from ..db import models as dbm
from . import types
from .connectionloaders import (
    EntityConnectionLoader,
    OneToManyRelationshipConnectionLoader,
)


def cabinet_node_from_db_model(o: dbm.Cabinet) -> "types.Cabinet":
    return types.Cabinet(db_id=o.id, id=o.uuid, name=o.name)


def drawer_node_from_db_model(o: dbm.Drawer) -> "types.Drawer":
    return types.Drawer(db_id=o.id, id=o.uuid, label=o.label)


class CabinetConnectionLoader(EntityConnectionLoader[dbm.Cabinet, "types.Cabinet"]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, dbm.Cabinet)

    def node_factory(self, db_entity: dbm.Cabinet) -> "types.Cabinet":
        return cabinet_node_from_db_model(db_entity)


class CabinetDrawerConnectionLoader(
    OneToManyRelationshipConnectionLoader[dbm.Drawer, "types.Drawer"]
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, dbm.Cabinet.drawers)

    def node_factory(self, db_entity: dbm.Drawer) -> "types.Drawer":
        return drawer_node_from_db_model(db_entity)
