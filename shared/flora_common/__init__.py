"""Shared utilities for all FloraAI services.

This package is deliberately tiny and dependency-light. Every service imports
the same config loader, logging setup, and a few cross-service schemas so that
the platform behaves consistently regardless of which module is running.
"""

from flora_common.logging import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
__version__ = "1.0.0"
