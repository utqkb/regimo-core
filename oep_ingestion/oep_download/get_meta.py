#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
get_meta

Fetches and persists metadata for all tables in the Open Energy Platform (OEP).

Author: GraphON Ingestion Team
Affiliation: Karlsruhe Institute of Technology (KIT)
License: MIT
Created: 2026-07-09
"""

import json
from pathlib import Path

import requests
from oep_client import OepClient

# === CONFIGURATION & LOGGER ==============================================
from config.oep_config import OEP_API_BASE, RAW_METADATA_DIR, SCHEMA
from oep_ingestion.shared import get_logger, setup_logging

log = get_logger("graphon_ingestion")


def download_all_metadata(output_dir: Path | None = None):
    """
    Fetch metadata for all tables in the configured OEP schema and persist as JSON files.

    Args:
        output_dir: Optional custom output directory. Defaults to RAW_METADATA_DIR / "oep_tables".
    """
    if output_dir is None:
        output_dir = RAW_METADATA_DIR / "oep_tables"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log.info(f"Fetching table list from schema '{SCHEMA}'...")
    
    # Fetch list of all tables using the advanced endpoint
    list_url = f"{OEP_API_BASE}/advanced/get_table_names"
    response = requests.post(list_url, json={"schema": SCHEMA})
    
    if response.status_code != 200:
        log.error(f"Failed to fetch table list: {response.text}")
        return
    
    tables = response.json()
    table_count = len(tables.get('content', []))
    log.info(f"Found {table_count} tables in schema '{SCHEMA}'. Starting metadata download...")
    
    # Initialize OEP client
    cli = OepClient()
    success_count = 0
    error_count = 0
    
    # Iterate through each table and fetch metadata
    for table_name in tables.get('content', []):
        try:
            log.debug(f"Fetching metadata for table: {table_name}")
            
            # Get metadata via OEP client
            metadata = cli.get_metadata(table_name)
            
            # Persist metadata as JSON file
            json_path = output_dir / f"{table_name}_metadata.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)
            
            success_count += 1
            log.debug(f"✓ Saved metadata for '{table_name}'")
            
        except Exception as e:
            error_count += 1
            log.error(f"Failed to download metadata for '{table_name}': {e}")
    
    log.info(f"Metadata download completed: {success_count} succeeded, {error_count} failed.")
    log.info(f"Output directory: {output_dir}")


if __name__ == '__main__':
    # Initialize logging once at entry point
    setup_logging("graphon_ingestion")
    download_all_metadata()
