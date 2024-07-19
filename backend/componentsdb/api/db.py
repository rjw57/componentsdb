import uuid

import sqlalchemy as sa

from ..db import models as dbm


def select_starting_at_uuid(model: dbm.Base, uuid: uuid.UUID):
    subquery = (
        sa.select(model.id).where(model.uuid == uuid).order_by(model.id.asc()).scalar_subquery()
    )
    return sa.select(model).where(model.id >= subquery)
