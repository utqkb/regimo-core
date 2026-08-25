#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Centralized logging configuration for the GraphON workspace.

Usage:
    Call setup_logging() once at your application entry point (CLI/main script).
    Use get_logger(name) in modules to obtain loggers.
    
Example:
    # In cli.py or main.py
    from shared_utils.logging_config import setup_logging, get_logger
    
    def main():
        setup_logging("graphon_ingestion")  # Configure once
        logger = get_logger(__name__)
        logger.info("Starting...")
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from shared_utils.project_handling import find_project_root


# Track which loggers have been configured to avoid duplicate handlers
_configured_loggers: set[str] = set()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    The logger name should typically be hierarchical, e.g.:
        - "graphon_ingestion" (package root)
        - "graphon_ingestion.cli" (cli module)
        - "graphon_analysis.neo_ingest_oep" (specific module)
    
    Call setup_logging() once before using loggers to configure handlers.
    """
    return logging.getLogger(name)


def setup_logging(
    project_name: str,
    log_dir: Path | None = None,
    level: int = logging.INFO,
    max_bytes: int = 1024 * 1024,  # 1MB
    backup_count: int = 5,
) -> None:
    """
    Configure logging for a project. Call once at application entry point.
    
    Args:
        project_name: Name for the logger and log file (e.g., "graphon_ingestion")
        log_dir: Directory for log files. Defaults to ./log next to pyproject.toml
        level: Logging level (default: INFO)
        max_bytes: Max size per log file before rotation (default: 1MB)
        backup_count: Number of backup files to keep (default: 5)
    
    This function is idempotent - calling it multiple times with the same
    project_name is safe and will not add duplicate handlers.
    """
    if project_name in _configured_loggers:
        return  # Already configured
    
    if log_dir is None:
        # Find project root by searching upward from caller's module location
        import inspect
        frame = inspect.stack()[1]
        caller_module = inspect.getmodule(frame[0])
        
        if caller_module and hasattr(caller_module, '__file__') and caller_module.__file__:
            current_path = Path(caller_module.__file__).resolve().parent
        else:
            current_path = Path.cwd()
        
        # Search upward for pyproject.toml
        project_root = None
        for parent in [current_path] + list(current_path.parents):
            if (parent / "pyproject.toml").exists():
                project_root = parent
                break
        
        if project_root:
            log_dir = project_root / "log"
        else:
            log_dir = Path.cwd() / "log"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{project_name}.log"
    
    # Get package logger
    logger = logging.getLogger(project_name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return
    
    # Format
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # File handler (rotating)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Attach handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Prevent log propagation to root (avoid duplicate output)
    logger.propagate = False
    
    _configured_loggers.add(project_name)
    logger.info(f"Logging configured at {log_file}")


__all__ = ["get_logger", "setup_logging", "_configured_loggers"]
