from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..logging import configure_logging
from . import graphql, healthcheck
from .settings import load_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    configure_logging(json_logging=settings.json_logging)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthcheck.router)
app.include_router(graphql.router, prefix="/graphql")
