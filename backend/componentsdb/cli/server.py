import sys
from typing import Annotated
from urllib.parse import quote

import requests
import structlog
import typer
import uvicorn

app = typer.Typer()


_structlog_foreign_pre_chain = [
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
]


def _make_logconfig(json_logging: bool = True):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": _structlog_foreign_pre_chain,
            },
            "console_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
                "foreign_pre_chain": _structlog_foreign_pre_chain,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console_formatter",
            },
            "json": {
                "class": "logging.StreamHandler",
                "formatter": "json_formatter",
            },
        },
        "loggers": {
            "": {
                "handlers": ["json"] if json_logging else ["console"],
                "propagate": True,
                "level": "INFO",
            },
        },
    }


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
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    uvicorn.run(
        "componentsdb.fastapi:app",
        host=host,
        port=port,
        reload=reload,
        log_config=_make_logconfig(json_logging=json_logging),
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
