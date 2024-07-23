import strawberry
from sqlalchemy.ext.asyncio import AsyncSession

from . import loaders
from .types import Query

schema = strawberry.Schema(query=Query)


def context_from_db_session(session: AsyncSession):
    return {
        "db_loaders": {
            "session": session,
            "cabinet": loaders.CabinetLoader(session),
            "related_cabinet": loaders.RelatedCabinetLoader(session),
            "cabinet_connection": loaders.CabinetConnectionFactory(session),
            "cabinet_drawer_connection": loaders.CabinetDrawerConnectionFactory(session),
            "drawer_collection_connection": loaders.DrawerCollectionConnectionFactory(session),
        }
    }
