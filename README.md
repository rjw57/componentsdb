# Components database

An experimental database for storing electronics components.

## Backend

### Installing dependencies

```sh
poetry -C backend install
```

### Generating migrations

```sh
docker compose run --rm alembic revision --autogenerate -m '... message ...'
```

### Running tests

```sh
poe -C test
```

Or, containerised,

```sh
docker compose run --rm backend-test
```
