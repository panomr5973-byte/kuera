"""KUERA AI — Unified logging setup.

Provides a consistent logging configuration across all modules.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

from .config import settings


def setup_logger(name: str = "KUERA") -> logging.Logger:
    """Create a logger with file + console handlers."""
    log_dir = settings.logs_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"unified_{datetime.now():%Y%m%d}.log"

    handler_file = logging.FileHandler(log_file, encoding="utf-8")
    handler_file.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    ))

    handler_console = logging.StreamHandler(sys.stdout)
    handler_console.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s"
    ))

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers on re-import
    if not logger.handlers:
        logger.addHandler(handler_file)
        logger.addHandler(handler_console)

    return logger
