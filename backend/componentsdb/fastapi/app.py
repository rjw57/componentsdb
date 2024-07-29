from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import graphql, healthcheck

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthcheck.router)
app.include_router(graphql.router, prefix="/graphql")
