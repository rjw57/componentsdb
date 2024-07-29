from typing import Optional

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter

from ..auth import AuthenticationProvider
from ..db.models import User
from ..graphql import make_context, schema
from .auth import get_auth_provider, get_authenticated_user
from .db import get_db_session


async def get_graphql_context(
    session: AsyncSession = Depends(get_db_session),
    auth_provider: AuthenticationProvider = Depends(get_auth_provider),
    authenticated_user: Optional[User] = Depends(get_authenticated_user),
):
    return make_context(
        db_session=session,
        authentication_provider=auth_provider,
        authenticated_user=authenticated_user,
    )


router: APIRouter = GraphQLRouter(schema, graphql_ide=None, context_getter=get_graphql_context)
