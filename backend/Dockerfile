FROM python:3.12-slim AS base
WORKDIR /usr/src/app/
RUN pip install poetry~=1.8 poetry-plugin-export~=1.8
COPY poetry.lock pyproject.toml .

FROM base AS alembic
RUN pip install alembic~=1.13 asyncpg==0.29 black~=23.1
WORKDIR /usr/src/app/
ENTRYPOINT ["alembic"]

FROM base AS deps
RUN \
  poetry export -f requirements.txt --output /tmp/requirements.txt && \
  pip install -r /tmp/requirements.txt && \
  rm /tmp/requirements.txt

# Run the componentsdb tooling for local development.
FROM base AS dev-tool
RUN poetry install --no-root
ENTRYPOINT ["poetry", "run", "python", "-m", "componentsdb.cli"]

# Run the componentsdb server with a healthcheck
FROM dev-tool AS dev
HEALTHCHECK \
  --interval=30s \
  --retries=5 \
  --start-period=120s \
  --start-interval=1s \
  CMD ["poetry", "run", "python", "-m", "componentsdb.cli", "server", "healthcheck"]
CMD ["server", "run"]

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
