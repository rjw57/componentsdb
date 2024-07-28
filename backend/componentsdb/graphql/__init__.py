import strawberry
from sqlalchemy.ext.asyncio import AsyncSession

from . import loaders
from .types import Mutation, Query

schema = strawberry.Schema(query=Query, mutation=Mutation)


def context_from_db_session(session: AsyncSession):
    return {
        "db_loaders": {
            "session": session,
            "cabinet": loaders.CabinetLoader(session),
            "related_cabinet": loaders.RelatedCabinetLoader(session),
            "related_drawer": loaders.RelatedDrawerLoader(session),
            "related_component": loaders.RelatedComponentLoader(session),
            "cabinet_connection": loaders.CabinetConnectionFactory(session),
            "cabinet_drawer_connection": loaders.CabinetDrawerConnectionFactory(session),
            "drawer_collection_connection": loaders.DrawerCollectionConnectionFactory(session),
            "component_collection_connection": loaders.ComponentCollectionConnectionFactory(
                session
            ),
        }
    }
