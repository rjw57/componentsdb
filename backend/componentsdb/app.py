import os
from typing import Literal

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import (
    AsyncTransaction,
    async_sessionmaker,
    create_async_engine,
)
from strawberry.fastapi import GraphQLRouter

from .graphql import context_from_db_session, schema

DB_ENGINE = create_async_engine(os.environ["SQLALCHEMY_DB_URL"], echo=True)
SESSION_MAKER = async_sessionmaker(DB_ENGINE, expire_on_commit=False)


async def get_db_transaction():
    async with SESSION_MAKER.begin() as tx:
        yield tx


async def get_graphql_context(db_tx: AsyncTransaction = Depends(get_db_transaction)):
    return context_from_db_session(db_tx)


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
