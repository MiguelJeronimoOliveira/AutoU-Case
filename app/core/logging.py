"""Logging configuration for the application."""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

