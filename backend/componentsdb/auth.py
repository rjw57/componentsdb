import dataclasses
import secrets
from collections.abc import Callable, Mapping
from datetime import timedelta
from typing import Annotated, Any, Literal, Optional

import sqlalchemy as sa
import structlog
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import bindparam

from .db.models import AccessToken, FederatedUserCredential, User
from .federatedidentity import async_validate_token

LOG = structlog.get_logger()


class AuthSettings(BaseSettings):
    token_lifetime: int = 3600
    federated_id_token_audience_issuer_pairs: list[tuple[str, str]] = Field(default_factory=list)

    model_config = SettingsConfigDict(env_prefix="AUTH_")


@dataclasses.dataclass
class JWTAuthorizationGrant:
    grant_type: Annotated[Literal["urn:ietf:params:oauth:grant-type:jwt-bearer"], Form()]
    assertion: Annotated[str, Form()]
    allow_sign_up: Annotated[bool, Form()] = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class AuthRouter(APIRouter):
    def __init__(
        self,
        *args,
        db_session_getter: Callable[..., AsyncSession],
        settings: Optional[AuthSettings] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        settings = settings if settings is not None else AuthSettings()

        SessionDep = Annotated[AsyncSession, Depends(db_session_getter)]

        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

        # TODO: error responses as per OAuth2 spec.
        @self.post("/token", response_model=TokenResponse)
        async def token(
            form_data: Annotated[JWTAuthorizationGrant, Depends()], db_session: SessionDep
        ):
            # TODO: jti
            try:
                claims = await async_validate_token(
                    form_data.assertion,
                    allowed_audience_and_issuers=settings.federated_id_token_audience_issuer_pairs,
                    required_claims=["aud", "iss", "sub"],
                )
            except Exception:
                LOG.exception("Error validating token")
                raise HTTPException(403, detail="invalid token")
            try:
                user = await user_from_federated_credential_claims(
                    db_session,
                    claims,
                    create_if_not_present=form_data.allow_sign_up,
                )
            except NoSuchUser:
                raise HTTPException(400, detail="no such user")
            access_token = await create_access_token(db_session, user, settings.token_lifetime)
            return TokenResponse(
                access_token=access_token.token, expires_in=settings.token_lifetime
            )

        @self.get("/userinfo")
        async def userinfo(token: Annotated[str, Depends(oauth2_scheme)], db_session: SessionDep):
            user = await user_or_none_from_access_token(db_session, token)
            if user is None:
                LOG.info("no user matches access token", token=token)
                raise HTTPException(403, detail="invalid token")
            return {"id": user.id}


async def user_or_none_from_access_token(session: AsyncSession, token: str) -> Optional[User]:
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


class NoSuchUser(RuntimeError):
    pass


async def user_from_federated_credential_claims(
    session: AsyncSession, claims: Mapping[str, Any], *, create_if_not_present=False
) -> User:
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

    # ... otherwise sign up the user with the new credentials.
    user = User()
    cred = FederatedUserCredential(
        user=user,
        audience=claims["aud"],
        issuer=claims["iss"],
        subject=claims["sub"],
    )
    session.add_all([user, cred])
    await session.flush([user, cred])
    return user
