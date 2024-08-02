FROM python:3.12-slim AS base
WORKDIR /usr/src/app/

FROM base AS poetry
RUN pip install poetry~=1.8 poetry-plugin-export~=1.8
COPY poetry.lock pyproject.toml .

FROM poetry AS deps
RUN \
  poetry export -f requirements.txt --output /tmp/requirements.txt && \
  pip install -r /tmp/requirements.txt && \
  rm /tmp/requirements.txt

# Run the componentsdb tooling for local development.
FROM poetry AS dev-tool
RUN poetry install --no-root
ENTRYPOINT ["poetry", "run", "python", "-m", "componentsdb.cli"]

FROM base AS alembic
RUN pip install alembic~=1.13 asyncpg==0.29 black~=23.1
ENTRYPOINT ["alembic"]

# Run the componentsdb server with a healthcheck
FROM dev-tool AS dev
HEALTHCHECK \
  --interval=30s \
  --retries=5 \
  --start-period=120s \
  --start-interval=1s \
  CMD ["poetry", "run", "python", "-m", "componentsdb.cli", "server", "healthcheck"]
CMD ["server", "dev"]

FROM deps AS prod
COPY ./ ./
RUN pip install -e .
ENTRYPOINT ["componentsdb"]
HEALTHCHECK \
  --interval=30s \
  --retries=5 \
  --start-period=120s \
  --start-interval=1s \
  CMD ["componentsdb", "server", "healthcheck"]
CMD ["server", "run"]
