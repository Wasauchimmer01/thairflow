import os
import logging
import logging.config
from logging.handlers import RotatingFileHandler


def setup_logging() -> None:
    """Configure application-wide logging.

    Creates a ``logs`` directory and configures both console and rotating file
    handlers writing to ``logs/app.log``. The log format and level are consistent
    across handlers.
    """
    os.makedirs("logs", exist_ok=True)

    logging_config = {
        "version": 1,
        "formatters": {
            "standard": {
                "format": "%(asctime)s %(levelname)-8s %(name)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "INFO",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "level": "INFO",
                "filename": "logs/app.log",
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    }

    logging.config.dictConfig(logging_config)
