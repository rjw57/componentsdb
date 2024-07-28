# Components database

An experimental database for storing electronics components.

## Getting started

1. [Install Task](https://taskfile.dev/installation/)
2. [Install pre-commit](https://pre-commit.com/#install)
3. Install pre-commit hooks, pull docker images, build containers and start the
   application:

    ```sh
    task
    ```

The application is available at http://localhost:3000/. The backend is available
at http://localhost:8000/.

## Tasks

Start application:

```sh
task up
```

Stop application:

```sh
task down
```

Stop application and remove volumes

```sh
task down-hard
```

## Database

Open a `psql` client on the database

```sh
task psql
```

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
poe -C backend test
```

Or, containerised,

```sh
docker compose run --rm backend-test
```

Or, via `task`,

```sh
task test
```
