from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter

from .graphql import schema


async def get_graphql_context():
    return {}


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
