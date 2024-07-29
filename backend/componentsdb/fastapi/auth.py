from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import AuthenticationProvider, AuthError
from ..db.models import User
from .db import get_db_session
from .settings import Settings, load_settings


def get_auth_provider(
    session: AsyncSession = Depends(get_db_session), settings: Settings = Depends(load_settings)
) -> AuthenticationProvider:
    return AuthenticationProvider(
        db_session=session,
        federated_identity_providers=settings.federated_identity_providers,
        access_token_lifetime=settings.access_token_lifetime,
    )


async def get_authenticated_user(
    auth_provider: AuthenticationProvider = Depends(get_auth_provider),
    authorization: Annotated[Optional[str], Header()] = None,
) -> Optional[User]:
    if authorization is None:
        return None
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(403, detail="bearer token required")
    access_token = authorization.split(" ")[1]
    try:
        return await auth_provider.authenticate_user_from_access_token(access_token)
    except AuthError as e:
        raise HTTPException(403, detail=str(e))
