"""GraphON Ingestion Module."""

__version__ = "0.1.0"

from oep_ingestion import neo_ingest_oep
from oep_ingestion.shared import get_logger
from shared_utils.logging_config import setup_logging

logger = get_logger(__name__)

__all__ = ["neo_ingest_oep", "get_logger", "setup_logging", "logger"]
