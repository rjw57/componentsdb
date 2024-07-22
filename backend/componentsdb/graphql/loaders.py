from sqlalchemy.ext.asyncio import AsyncSession

from ..db import models as dbm
from . import types
from .connectionloaders import (
    EntityConnectionLoader,
    OneToManyRelationshipConnectionLoader,
)


class CabinetConnectionLoader(EntityConnectionLoader[dbm.Cabinet, "types.Cabinet"]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, dbm.Cabinet)

    def node_factory(self, db_entity: dbm.Cabinet) -> "types.Cabinet":
        return types.Cabinet(db_id=db_entity.id, id=db_entity.uuid, name=db_entity.name)


class CabinetDrawerConnectionLoader(
    OneToManyRelationshipConnectionLoader[dbm.Drawer, "types.Drawer"]
):
    def __init__(self, session: AsyncSession):
        super().__init__(session, dbm.Cabinet.drawers)

    def node_factory(self, db_entity: dbm.Drawer) -> "types.Drawer":
        return types.Drawer(db_id=db_entity.id, id=db_entity.uuid, label=db_entity.label)
