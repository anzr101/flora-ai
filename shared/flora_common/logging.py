"""Structured, JSON-friendly logging shared by every FloraAI service.

We avoid pulling in a heavy logging framework; the stdlib `logging` module with
a consistent formatter is enough and keeps container images small. Logs are
emitted as single-line key/value records which are easy to grep locally and
ship to a log aggregator in production.
"""

from __future__ import annotations

import logging
import os
import sys

_CONFIGURED = False


def configure_logging(level: str | None = None) -> None:
    """Configure the root logger once, idempotently.

    Safe to call from every service entrypoint; subsequent calls are no-ops so
    we never attach duplicate handlers (a common cause of doubled log lines).
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = (level or os.getenv("FLORA_LOG_LEVEL", "INFO")).upper()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s level=%(levelname)s logger=%(name)s msg=%(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Tame noisy third-party loggers that would otherwise drown our own.
    for noisy in ("httpx", "urllib3", "sentence_transformers", "chromadb"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for `name`, ensuring logging is set up."""
    configure_logging()
    return logging.getLogger(name)
