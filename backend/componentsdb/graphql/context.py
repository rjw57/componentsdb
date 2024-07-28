from functools import cached_property

from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import AuthenticationProvider
from . import loaders


class DbContext:
    db_session: AsyncSession

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    @cached_property
    def cabinet(self) -> loaders.CabinetLoader:
        return loaders.CabinetLoader(self.db_session)

    @cached_property
    def related_cabinet(self) -> loaders.RelatedCabinetLoader:
        return loaders.RelatedCabinetLoader(self.db_session)

    @cached_property
    def related_drawer(self) -> loaders.RelatedDrawerLoader:
        return loaders.RelatedDrawerLoader(self.db_session)

    @cached_property
    def related_component(self) -> loaders.RelatedComponentLoader:
        return loaders.RelatedComponentLoader(self.db_session)

    @cached_property
    def cabinet_connection(self) -> loaders.CabinetConnectionFactory:
        return loaders.CabinetConnectionFactory(self.db_session)

    @cached_property
    def cabinet_drawer_connection(self) -> loaders.CabinetDrawerConnectionFactory:
        return loaders.CabinetDrawerConnectionFactory(self.db_session)

    @cached_property
    def drawer_collection_connection(self) -> loaders.DrawerCollectionConnectionFactory:
        return loaders.DrawerCollectionConnectionFactory(self.db_session)

    @cached_property
    def component_collection_connection(self) -> loaders.ComponentCollectionConnectionFactory:
        return loaders.ComponentCollectionConnectionFactory(self.db_session)


def make_context(db_session: AsyncSession, authentication_provider: AuthenticationProvider):
    return {
        "db": DbContext(db_session),
        "auth": authentication_provider,
    }
