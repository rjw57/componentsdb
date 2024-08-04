import asyncio
from functools import cached_property
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import AuthenticationProvider
from ..db import models as dbm
from . import loaders


class DbContext:
    db_session: AsyncSession
    db_lock: asyncio.Lock

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.db_lock = asyncio.Lock()

    @cached_property
    def cabinet(self) -> loaders.CabinetLoader:
        return loaders.CabinetLoader(self.db_session, self.db_lock)

    @cached_property
    def related_cabinet(self) -> loaders.RelatedCabinetLoader:
        return loaders.RelatedCabinetLoader(self.db_session, self.db_lock)

    @cached_property
    def related_drawer(self) -> loaders.RelatedDrawerLoader:
        return loaders.RelatedDrawerLoader(self.db_session, self.db_lock)

    @cached_property
    def related_component(self) -> loaders.RelatedComponentLoader:
        return loaders.RelatedComponentLoader(self.db_session, self.db_lock)

    @cached_property
    def cabinet_connection(self) -> loaders.CabinetConnectionFactory:
        return loaders.CabinetConnectionFactory(self.db_session, self.db_lock)

    @cached_property
    def cabinet_drawer_connection(self) -> loaders.CabinetDrawerConnectionFactory:
        return loaders.CabinetDrawerConnectionFactory(self.db_session, self.db_lock)

    @cached_property
    def drawer_collection_connection(self) -> loaders.DrawerCollectionConnectionFactory:
        return loaders.DrawerCollectionConnectionFactory(self.db_session, self.db_lock)

    @cached_property
    def component_collection_connection(self) -> loaders.ComponentCollectionConnectionFactory:
        return loaders.ComponentCollectionConnectionFactory(self.db_session, self.db_lock)

    @cached_property
    def component_connection(self) -> loaders.ComponentConnectionFactory:
        return loaders.ComponentConnectionFactory(self.db_session, self.db_lock)


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
