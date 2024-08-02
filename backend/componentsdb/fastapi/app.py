import secrets
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from ..logging import configure_logging
from . import graphql, healthcheck
from .settings import load_settings

LOG = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    configure_logging(json_logging=settings.json_logging)
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    with structlog.contextvars.bound_contextvars(request_id=secrets.token_urlsafe()):
        start = time.monotonic()
        response: Response = await call_next(request)
        stop = time.monotonic()
        LOG.info(
            f"{request.method} {request.url.path} {response.status_code}",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=(stop - start) * 1e3,
        )

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthcheck.router)
app.include_router(graphql.router, prefix="/graphql")
