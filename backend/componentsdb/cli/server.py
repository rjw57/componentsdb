import os
import sys
from typing import Annotated
from urllib.parse import quote

import requests
import typer
import uvicorn

from componentsdb.logging import configure_logging, make_logconfig

app = typer.Typer()


@app.command()
def run(
    host: Annotated[str, typer.Option(envvar="HOST")] = "0.0.0.0",
    port: Annotated[int, typer.Option(envvar="PORT")] = 8000,
    reload: bool = False,
    json_logging: bool = True,
):
    """
    Run a production-ready server.
    """
    configure_logging(json_logging)

    # HACK: pass logging config down to wrapped app.
    os.environ["JSON_LOGGING"] = "true" if json_logging else "false"

    uvicorn.run(
        "componentsdb.fastapi:app",
        host=host,
        port=port,
        reload=reload,
        log_config=make_logconfig(json_logging=json_logging),
    )


@app.command()
def dev(
    host: Annotated[str, typer.Option(envvar="HOST")] = "127.0.0.1",
    port: Annotated[int, typer.Option(envvar="PORT")] = 8000,
):
    """
    Run a local development server.

    This acts like the run command except that auto-reload and human readable logging is enabled.
    The default bind address is 127.0.0.1 to guard against opening your development server to the
    local network.
    """
    run(host=host, port=port, reload=True, json_logging=False)


@app.command()
def healthcheck(
    host: Annotated[str, typer.Option(envvar="HOST")] = "127.0.0.1",
    port: Annotated[int, typer.Option(envvar="PORT")] = 8000,
):
    """
    Check if the server is running.

    Exits with a non-zero exit code if there is an error connecting to the server on the host and
    port specified. Exits with a zero exit code otherwise.
    """
    url = f"http://{quote(host)}:{port}/healthy"
    r = requests.get(url, timeout=1)
    if r.status_code >= 400:
        sys.exit(1)
