"""
DocuMind AI — Logging Configuration
Structured logging setup using Python's standard logging module.
"""

import logging
import sys
from typing import Optional

from app.core.config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure application-wide logging.

    Args:
        log_level: Override log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   Defaults to the value from settings.
    """
    level_str = (log_level or settings.log_level).upper()
    level = getattr(logging, level_str, logging.INFO)

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
        if settings.is_development
        else "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logger = logging.getLogger("documind")
    logger.info("Logging initialized at level: %s", level_str)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger under the 'documind' namespace.

    Usage:
        logger = get_logger(__name__)
        logger.info("Processing document: %s", doc_id)
    """
    return logging.getLogger(f"documind.{name}")
