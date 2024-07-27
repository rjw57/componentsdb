import os
from typing import Literal

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from strawberry.fastapi import GraphQLRouter

from .auth import AuthRouter
from .graphql import context_from_db_session, schema

DB_ENGINE = create_async_engine(os.environ["SQLALCHEMY_DB_URL"], echo=True)
SESSION_MAKER = async_sessionmaker(DB_ENGINE, expire_on_commit=False)


async def get_db_session():
    async with SESSION_MAKER.begin() as session:
        try:
            yield session
            await session.flush()
        except Exception as e:
            await session.rollback()
            raise e
        else:
            await session.commit()


async def get_graphql_context(session: AsyncSession = Depends(get_db_session)):
    return context_from_db_session(session)


graphql_app: APIRouter = GraphQLRouter(
    schema, graphql_ide=None, context_getter=get_graphql_context
)

app = FastAPI()
app.include_router(AuthRouter(tags=["auth"], db_session_getter=get_db_session))

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
