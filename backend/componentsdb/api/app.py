from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, FastAPI, Path
from pydantic import Field
from strawberry.fastapi import GraphQLRouter

from ..graphql import schema
from . import models as m

app = FastAPI(
    title="Components Database",
    version="0.1.0",
)

graphql: APIRouter = GraphQLRouter(schema)
app.include_router(graphql, prefix="/graphql")


@app.get("/cabinets", response_model=m.CabinetList, tags=["cabinet"])
def cabinets_list(
    cursor: Optional[UUID] = None,
    limit: Optional[Annotated[int, Field(strict=True, ge=1, le=100)]] = 100,
) -> m.CabinetList:
    raise NotImplementedError()


@app.get("/cabinets/{cabinetId}", response_model=m.CabinetDetail, tags=["cabinet"])
def cabinet_get(cabinet_id: Annotated[UUID, Path(alias="cabinetId")]) -> m.CabinetDetail:
    raise NotImplementedError()


@app.get("/status", response_model=m.ServerStatus, tags=["status"])
def status_get() -> m.ServerStatus:
    return m.ServerStatus()
