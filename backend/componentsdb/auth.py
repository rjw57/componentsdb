import secrets
from collections.abc import Mapping
from datetime import timedelta
from typing import Any, Optional

import sqlalchemy as sa
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import bindparam

from .db.models import AccessToken, FederatedUserCredential, User


class FederatedIdentityProvider(BaseModel):
    issuer: str
    audience: str


class AuthSettings(BaseSettings):
    token_lifetime: int = 3600
    federated_identity_providers: dict[str, FederatedIdentityProvider] = Field(
        default_factory=dict
    )


class NoSuchUser(RuntimeError):
    "No user matching the credentials could be found."


async def user_or_none_from_access_token(session: AsyncSession, token: str) -> Optional[User]:
    """
    Query the user matching the passed access token. If the access token is expired, no user is
    returned.

    Args:
        session: the database session
        token: the access token

    Returns: the matching user or None if the access token is invalid or has expired.
    """
    return (
        await session.execute(
            sa.select(User)
            .join(AccessToken)
            .where(
                AccessToken.expires_at >= sa.func.now(),
                AccessToken.token == token,
            )
        )
    ).scalar_one_or_none()


async def create_access_token(session: AsyncSession, user: User, expires_in: int) -> AccessToken:
    """
    Create a new access token for the passed user. The access token is added to the current
    database session and flushed to the connection.

    Args:
        session: the database session
        user: the user to create an access token for
        expires_in: the number of seconds from now that the token should expire

    Returns: the newly created access token.
    """
    access_token = AccessToken(
        token=secrets.token_urlsafe(32),
        user=user,
        expires_at=sa.func.date_add(
            sa.func.now(),
            bindparam("expires_in", timedelta(seconds=expires_in), sa.Interval(native=True)),
        ),
    )
    session.add(access_token)
    await session.flush([access_token])
    return access_token


async def user_from_federated_credential_claims(
    session: AsyncSession, claims: Mapping[str, Any], *, create_if_not_present=False
) -> User:
    """
    Find user in database given the claims from a federated credential.

    Args:
        session: database session
        claims: claims from federated credential
        create_if_not_present: if True, create the user if they don't exist, populating the profile
            from the credential.

    Returns: the authenticated user

    Raises:
        NoSuchUser: if no matching user can be found and create_if_not_present is False.
    """
    # Search for a user matching the federated credential.
    user = (
        await session.execute(
            sa.select(User)
            .join(FederatedUserCredential)
            .where(
                FederatedUserCredential.audience == claims["aud"],
                FederatedUserCredential.issuer == claims["iss"],
                FederatedUserCredential.subject == claims["sub"],
            )
        )
    ).scalar_one_or_none()
    if user is not None:
        return user

    # If there is no match and we shouldn't create one, moan.
    if not create_if_not_present:
        raise NoSuchUser("No user matches the federated credential provided.")

    # ... otherwise sign up the user with the new credentials populating the profile from the
    # claims.
    user = User(
        email=claims.get("email", None),
        email_verified=bool(claims.get("email_verified", False)),
        display_name=claims.get("name", claims["sub"]),
        avatar_url=claims.get("picture", None),
    )
    cred = FederatedUserCredential(
        user=user,
        audience=claims["aud"],
        issuer=claims["iss"],
        subject=claims["sub"],
        most_recent_claims=claims,
    )
    session.add_all([user, cred])
    await session.flush([user, cred])
    return user
