import structlog

_common_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
    structlog.processors.format_exc_info,
    structlog.processors.TimeStamper(fmt="iso"),
]


def configure_logging(json_logging: bool = True):
    structlog.configure(
        processors=(
            _common_processors
            + [
                (
                    structlog.processors.JSONRenderer()
                    if json_logging
                    else structlog.dev.ConsoleRenderer()
                )
            ]
        ),
        logger_factory=structlog.PrintLoggerFactory(),
    )


def make_logconfig(json_logging: bool = True):
    foreign_pre_chain = [
        structlog.stdlib.add_logger_name,
    ] + _common_processors
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": foreign_pre_chain,
            },
            "console_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
                "foreign_pre_chain": foreign_pre_chain,
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
