"""GraphON Ingestion Shared Utilities."""

from shared_utils.logging_config import get_logger, setup_logging


PROJECT_LOGGER_NAME = "graphon_ingestion"

__all__ = ["PROJECT_LOGGER_NAME", "get_logger", "setup_logging"]
