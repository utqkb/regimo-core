"""GraphON OEP Analysis Module."""

from shared_utils.logging_config import get_logger

PROJECT_LOGGER_NAME = "graphon_analysis"

logger = get_logger(PROJECT_LOGGER_NAME)

__all__ = ["logger", "get_logger", "PROJECT_LOGGER_NAME"]
