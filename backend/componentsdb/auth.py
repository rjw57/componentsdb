import dataclasses
import secrets
from collections.abc import Mapping
from datetime import timedelta
from typing import Any, Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import bindparam

from .db.models import AccessToken, FederatedUserCredential, RefreshToken, User


@dataclasses.dataclass
class FederatedIdentityProvider:
    issuer: str
    audience: str


class AuthError(RuntimeError):
    "Base class for all authentication errors"


class InvalidAccessTokenError(AuthError):
    "Provided access token could not be validated"


class InvalidRefreshTokenError(AuthError):
    "Provided refresh token could not be validated"


class UserAlreadySignedUp(AuthError):
    "The requested user has already signed up"


class InvalidProvider(AuthError):
    "The requested federated identity provider does not exist."


class NoSuchUser(AuthError):
    "No user matching the credentials could be found."


class AuthenticationProvider:
    DEFAULT_ACCESS_TOKEN_LIFETIME = 3600  # 1 hr
    DEFAULT_REFRESH_TOKEN_LIFETIME = 7 * 24 * 60 * 3600  # 1 wk

    db_session: AsyncSession
    federated_identity_providers: Mapping[str, FederatedIdentityProvider]
    access_token_lifetime: int
    refresh_token_lifetime: int

    def __init__(
        self,
        db_session: AsyncSession,
        federated_identity_providers: Optional[Mapping[str, FederatedIdentityProvider]] = None,
        access_token_lifetime: int = DEFAULT_ACCESS_TOKEN_LIFETIME,
        refresh_token_lifetime: int = DEFAULT_REFRESH_TOKEN_LIFETIME,
    ):
        self.db_session = db_session
        self.federated_identity_providers = (
            federated_identity_providers if federated_identity_providers is not None else dict()
        )
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime

    async def create_user_with_federated_identity(self, provider: str, id_token: str) -> User:
        """
        Sign up a new user based on a federated id token.

        Args:
            provider: federated identity provider to use. This must be one of the keys from the
               federated_identity_providers attribute.
            id_token: an id token issued by the federated identity provider.

        Returns: the newly created user.

        Raises:
            FederatedIdentityError: the provided id token was invalid
            InvalidProvider: the selected provider does not exist
            UserAlreadySignedUp: the user was already signed up
        """
        raise NotImplementedError()

    async def user_credentials_from_federated_identity(
        self, provider: str, id_token: str
    ) -> tuple[User, AccessToken, RefreshToken]:
        """
        Return credentials for an existing user based on a federated id token.

        Args:
            provider: federated identity provider to use. This must be one of the keys from the
               federated_identity_providers attribute.
            id_token: an id token issued by the federated identity provider

        Returns: the user corresponding to the federated identity credentials, a short lived access
            token and a longer lived refresh token. The lifetime of the access and refresh tokens
            can be retrieved via the access_token_lifetime and refresh_token_lifetime attributes.

        Raises:
            FederatedIdentityError: the provided id token was invalid
            InvalidProvider: the selected provider does not exist
            NoSuchUser: no user matching the federated identity provider credentials was found
        """
        raise NotImplementedError()

    async def user_credentials_from_refresh_token(
        self, refresh_token: str
    ) -> tuple[User, AccessToken, RefreshToken]:
        """
        Return credentials for an existing user based on a refresh token.

        Args:
            refresh_token: a previously issued refresh token.

        Returns: the user corresponding to the refresh token, a short lived access token and a
            new longer lived refresh token. The lifetime of the access and refresh tokens
            can be retrieved via the access_token_lifetime and refresh_token_lifetime attributes.

        Raises:
            InvalidRefreshTokenError: the refresh token provided does not exist, has expired or was
                previously used.
        """
        raise NotImplementedError()

    async def authenticate_user_from_access_token(self, access_token: str) -> User:
        """
        Authenticate a user given an access token.

        Args:
            access_token: access token provided by the incoming request.

        Returns: the authenticated user

        Raises:
            InvalidAccessTokenError: the provided access token does not exist or has expired.
        """
        user = (
            await self.db_session.execute(
                sa.select(User)
                .join(AccessToken)
                .where(
                    AccessToken.expires_at >= sa.func.now(),
                    AccessToken.token == access_token,
                )
            )
        ).scalar_one_or_none()
        if user is None:
            raise InvalidAccessTokenError("The access token could not be verified")
        return user

    def _create_user_credentials(self, user: User) -> tuple[AccessToken, RefreshToken]:
        access_token = create_access_token(self.db_session, user, self.access_token_lifetime)
        refresh_token = create_refresh_token(self.db_session, user, self.refresh_token_lifetime)
        return access_token, refresh_token


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


def create_access_token(session: AsyncSession, user: User, expires_in: int) -> AccessToken:
    """
    Create a new access token for the passed user. The access token is added to the current
    database session.

    Args:
        session: the database session
        user: the user to create an access token for
        expires_in: the number of seconds from now that the token should expire

    Returns: the newly created access token.
    """
    access_token = AccessToken(
        token=secrets.token_urlsafe(64),
        user=user,
        expires_at=sa.func.date_add(
            sa.func.now(),
            bindparam("expires_in", timedelta(seconds=expires_in), sa.Interval(native=True)),
        ),
    )
    session.add(access_token)
    return access_token


def create_refresh_token(session: AsyncSession, user: User, expires_in: int) -> RefreshToken:
    """
    Create a new refresh token for the passed user. The refresh token is added to the current
    database session.

    Args:
        session: the database session
        user: the user to create an refresh token for
        expires_in: the number of seconds from now that the token should expire

    Returns: the newly created refresh token.
    """
    refresh_token = RefreshToken(
        token=secrets.token_urlsafe(64),
        user=user,
        expires_at=sa.func.date_add(
            sa.func.now(),
            bindparam("expires_in", timedelta(seconds=expires_in), sa.Interval(native=True)),
        ),
    )
    session.add(refresh_token)
    return refresh_token


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
