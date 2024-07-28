import dataclasses
import secrets
from collections.abc import Mapping
from datetime import timedelta
from typing import Any, Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import bindparam

from .db.models import AccessToken, FederatedUserCredential, RefreshToken, User
from .federatedidentity import AsyncOIDCTokenIssuer


@dataclasses.dataclass
class FederatedIdentityProvider:
    issuer: str
    audience: str


@dataclasses.dataclass
class UserCredentials:
    user: User
    access_token: str
    refresh_token: str


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
    federated_identity_providers: Mapping[str, AsyncOIDCTokenIssuer]
    access_token_lifetime: int
    refresh_token_lifetime: int

    def __init__(
        self,
        db_session: AsyncSession,
        federated_identity_providers: Optional[Mapping[str, FederatedIdentityProvider]] = None,
        access_token_lifetime: int = DEFAULT_ACCESS_TOKEN_LIFETIME,
        refresh_token_lifetime: int = DEFAULT_REFRESH_TOKEN_LIFETIME,
    ):
        federated_identity_providers = (
            federated_identity_providers if federated_identity_providers is not None else dict()
        )
        self.db_session = db_session
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime
        self.federated_identity_providers = {
            k: AsyncOIDCTokenIssuer(issuer=v.issuer, audience=v.audience)
            for k, v in federated_identity_providers.items()
        }

    async def create_user_from_federated_credential(self, provider: str, credential: str) -> User:
        """
        Sign up a new user based on a federated identity provider credential.

        Args:
            provider: federated identity provider to use. This must be one of the keys from the
               federated_identity_providers attribute.
            credential: an id token issued by the federated identity provider.

        Returns: the newly created user.

        Raises:
            FederatedIdentityError: the provided id token was invalid
            InvalidProvider: the selected provider does not exist
            UserAlreadySignedUp: the user was already signed up
        """
        user, claims = await self._query_user_from_federated_credential(provider, credential)
        if user is not None:
            raise UserAlreadySignedUp("user already registered with that identity")
        return await self._create_user_for_federated_credential_claims(claims)

    async def user_credentials_from_federated_credential(
        self, provider: str, credential: str
    ) -> UserCredentials:
        """
        Return credentials for an existing user based on a federated identity provider credential.

        Args:
            provider: federated identity provider to use. This must be one of the keys from the
               federated_identity_providers attribute.
            credential: an id token issued by the federated identity provider

        Returns: user credentials for the user corresponding to the federated identity credentials.

        Raises:
            FederatedIdentityError: the provided id token was invalid
            InvalidProvider: the selected provider does not exist
            NoSuchUser: no user matching the federated identity provider credentials was found
        """
        user, _ = await self._query_user_from_federated_credential(provider, credential)
        if user is None:
            raise NoSuchUser("no user matches the provided federated credential")

        return await self.create_user_credentials(user)

    async def user_credentials_from_refresh_token(self, refresh_token: str) -> UserCredentials:
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
        user_id = (
            await self.db_session.execute(
                sa.update(RefreshToken)
                .where(
                    RefreshToken.expires_at >= sa.func.now(),
                    RefreshToken.token == refresh_token,
                    RefreshToken.used_at.is_(None),
                )
                .values(used_at=sa.func.now())
                .returning(RefreshToken.user_id)
            )
        ).scalar_one_or_none()
        if user_id is None:
            raise InvalidRefreshTokenError("The refresh token could not be verified")
        return await self.create_user_credentials(
            (await self.db_session.execute(sa.select(User).where(User.id == user_id))).scalar_one()
        )

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

    async def create_user_credentials(self, user: User) -> UserCredentials:
        """
        Create access credentials for the passed user.

        Args:
            user: user to create credentials for

        Returns: access credentials for the user.
        """
        access_token = AccessToken(
            token=secrets.token_urlsafe(64),
            user=user,
            expires_at=sa.func.date_add(
                sa.func.now(),
                bindparam(
                    "expires_in",
                    timedelta(seconds=self.access_token_lifetime),
                    sa.Interval(native=True),
                ),
            ),
        )
        refresh_token = RefreshToken(
            token=secrets.token_urlsafe(64),
            user=user,
            expires_at=sa.func.date_add(
                sa.func.now(),
                bindparam(
                    "expires_in",
                    timedelta(seconds=self.refresh_token_lifetime),
                    sa.Interval(native=True),
                ),
            ),
        )
        self.db_session.add_all([access_token, refresh_token])
        await self.db_session.flush([access_token, refresh_token])
        return UserCredentials(
            user=user, access_token=access_token.token, refresh_token=refresh_token.token
        )

    async def _query_user_from_federated_credential(
        self, provider: str, credential: str
    ) -> tuple[Optional[User], Mapping[str, Any]]:
        """
        Find user in database given a federated identity provider credential.

        Args:
            provider: federated identity provider to use. This must be one of the keys from the
               federated_identity_providers attribute.
            credential: an id token issued by the federated identity provider

        Returns: the authenticated user, or None if no user could be found, and the verified claims
            from the id token.

        Raises:
            FederatedIdentityError: the provided id token was invalid
            InvalidProvider: the selected provider does not exist
        """
        try:
            fip = self.federated_identity_providers[provider]
        except KeyError:
            raise InvalidProvider(f"No such provider: {provider}")

        await fip.prepare()
        claims = fip.validate(credential)

        user = (
            await self.db_session.execute(
                sa.select(User)
                .join(FederatedUserCredential)
                .where(
                    FederatedUserCredential.audience == claims["aud"],
                    FederatedUserCredential.issuer == claims["iss"],
                    FederatedUserCredential.subject == claims["sub"],
                )
            )
        ).scalar_one_or_none()

        return user, claims

    async def _create_user_for_federated_credential_claims(self, claims: Mapping[str, Any]):
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
        self.db_session.add_all([user, cred])
        await self.db_session.flush([user, cred])
        return user
