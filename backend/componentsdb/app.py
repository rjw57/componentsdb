from typing import Annotated, Literal, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from strawberry.fastapi import GraphQLRouter

from .auth import AuthenticationProvider, AuthError, FederatedIdentityProvider
from .db.models import User
from .federatedidentity import FederatedIdentityError
from .graphql import make_context, schema


class Settings(BaseSettings):
    sqlalchemy_db_url: str
    access_token_lifetime: int = 3600
    federated_identity_providers: dict[str, FederatedIdentityProvider] = Field(
        default_factory=dict
    )


def load_settings() -> Settings:
    return Settings()


async def get_db_session(settings: Settings = Depends(load_settings)):
    db_engine = create_async_engine(settings.sqlalchemy_db_url)
    session_maker = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_maker.begin() as session:
        try:
            yield session
            await session.flush()
        except Exception as e:
            await session.rollback()
            raise e
        else:
            await session.commit()


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
    except (AuthError, FederatedIdentityError) as e:
        raise HTTPException(403, detail=str(e))


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


graphql_app: APIRouter = GraphQLRouter(
    schema, graphql_ide=None, context_getter=get_graphql_context
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


@app.get("/healthy")
def healthy() -> HealthResponse:
    return HealthResponse()


app.include_router(graphql_app, prefix="/graphql")
