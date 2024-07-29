import enum
from typing import Annotated, Any, Optional, Union

import strawberry
from strawberry.field_extensions import InputMutationExtension

from .. import auth
from ..db import models as dbm
from .paginationtypes import Node


def _auth_provider(context_: dict[str, Any]) -> auth.AuthenticationProvider:
    auth_provider = context_.get("authentication_provider")
    if auth_provider is None or not isinstance(auth_provider, auth.AuthenticationProvider):
        raise ValueError(
            "context has no AuthenticationProvider instance available via the "
            "'authentication_provider' key"
        )
    return auth_provider


def _authenticated_user(context_: dict[str, Any]) -> Optional[dbm.User]:
    user = context_.get("authenticated_user")
    if user is not None and not isinstance(user, dbm.User):
        raise ValueError("authenticated user in context is not a database User model")
    return user


@strawberry.type
class User(Node):
    db_resource: strawberry.Private[dbm.User]
    email: Optional[str]
    email_verified: bool
    display_name: str
    avatar_url: Optional[str]

    @classmethod
    def from_db_model(cls, user: dbm.User):
        return cls(
            db_resource=user,
            id=user.uuid,
            email=user.email,
            email_verified=user.email_verified,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
        )


@strawberry.type
class UserCredentials:
    user: User
    access_token: str
    refresh_token: str
    expires_in: int

    @classmethod
    def from_auth_user_credentials(cls, credentials: auth.UserCredentials):
        return cls(
            user=User.from_db_model(credentials.user),
            access_token=credentials.access_token,
            refresh_token=credentials.refresh_token,
            expires_in=credentials.access_token_lifetime,
        )


@strawberry.type
class FederatedIdentityProvider:
    name: str
    audience: str
    issuer: str


@strawberry.enum
class AuthErrorType(enum.StrEnum):
    NO_SUCH_FEDERATED_IDENTITY_PROVIDER = enum.auto()
    INVALID_FEDERATED_CREDENTIAL = enum.auto()
    INVALID_CREDENTIAL = enum.auto()
    USER_ALREADY_SIGNED_UP = enum.auto()


@strawberry.type
class AuthError:
    error: AuthErrorType
    detail: str


@strawberry.type
class AuthQueries:
    @strawberry.field
    def federated_identity_providers(
        self, info: strawberry.Info
    ) -> list[FederatedIdentityProvider]:
        return [
            FederatedIdentityProvider(name=k, audience=v.audience, issuer=v.issuer)
            for k, v in _auth_provider(info.context).federated_identity_providers.items()
        ]

    @strawberry.field
    def authenticated_user(self, info: strawberry.Info) -> Optional[User]:
        user = _authenticated_user(info.context)
        if user is None:
            return None
        return User.from_db_model(user)


@strawberry.type
class AuthMutations:
    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def credentials_from_federated_credential(
        self, info: strawberry.Info, provider: str, credential: str, is_new_user: bool = False
    ) -> Annotated[Union[UserCredentials, AuthError], strawberry.union("AuthCredentialsResponse")]:
        auth_provider = _auth_provider(info.context)
        try:
            if is_new_user:
                credentials = await auth_provider.create_user_from_federated_credential(
                    provider, credential
                )
            else:
                credentials = await auth_provider.user_credentials_from_federated_credential(
                    provider, credential
                )
        except auth.InvalidProvider as e:
            return AuthError(
                error=AuthErrorType.NO_SUCH_FEDERATED_IDENTITY_PROVIDER, detail=str(e)
            )
        except auth.InvalidFederatedCredential as e:
            return AuthError(error=AuthErrorType.INVALID_FEDERATED_CREDENTIAL, detail=str(e))
        except auth.UserAlreadySignedUp as e:
            return AuthError(error=AuthErrorType.USER_ALREADY_SIGNED_UP, detail=str(e))
        return UserCredentials.from_auth_user_credentials(credentials)

    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def refresh_credentials(
        self, info: strawberry.Info, refresh_token: str
    ) -> Annotated[Union[UserCredentials, AuthError], strawberry.union("AuthCredentialsResponse")]:
        auth_provider = _auth_provider(info.context)
        try:
            return UserCredentials.from_auth_user_credentials(
                await auth_provider.user_credentials_from_refresh_token(refresh_token)
            )
        except auth.InvalidRefreshTokenError as e:
            return AuthError(error=AuthErrorType.INVALID_CREDENTIAL, detail=str(e))
