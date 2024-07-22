import strawberry
from sqlalchemy.ext.asyncio import AsyncSession

from . import loaders
from .types import Query

schema = strawberry.Schema(query=Query)


def context_from_db_session(session: AsyncSession):
    return {
        "db_loaders": {
            "cabinet_connection": loaders.CabinetConnectionLoader(session),
            "cabinet_drawer_connection": loaders.CabinetDrawerConnectionLoader(session),
        }
    }
