import strawberry
from sqlalchemy.ext.asyncio import AsyncSession

from .context import DbContext
from .types import Mutation, Query

schema = strawberry.Schema(query=Query, mutation=Mutation)


def make_context(session: AsyncSession):
    return {
        "db": DbContext(session),
    }
