#!/usr/bin/env python3
"""
preprocess_data

Automated metadata pre-processing, validation pipeline, and schema correction
utility for Open Energy Platform (OEP) records. It validates dataset instances
against a LinkML schema, dynamically resolves missing fields or table column definitions
via the OEP REST API, and applies structured annotations to maintain FAIR data compliance.

Author: Mohamed Anis Koubaa
Affiliation: Karlsruhe Institute of Technology (KIT)
License: MIT
Created: 2026-07-20
"""

import json
from pathlib import Path

import requests
import yaml
from linkml.validator import validate

# === CONFIGURATION & LOGGER ==============================================
from config.oep_config import (
    METADATA_DIR,
    RAW_METADATA_DIR,
    SCHEMA_PATH,
)
from oep_ingestion.shared import get_logger

log = get_logger("preprocess_data")

# OEP API Configuration
OEP_API_BASE = "https://openenergyplatform.org/api/v0"
DEFAULT_TIMEOUT = 10
MAX_ORDINAL_POSITION = 9999

def load_metadata_file(file_path):
    """Loads a metadata file based on its extension (JSON or YAML)."""
    with open(file_path, "r", encoding="utf-8") as f:
        if file_path.suffix.lower() == ".json":
            return json.load(f)
        else:
            return yaml.safe_load(f)


def _extract_fields_from_api_response(api_data: dict | list) -> list[dict]:
    """Extract field definitions from OEP API response."""
    fields = []
    
    if not isinstance(api_data, dict):
        return fields
    
    # Sort columns by their ordinal position if available
    sorted_cols = sorted(
        api_data.items(),
        key=lambda x: x[1].get("ordinal_position", MAX_ORDINAL_POSITION)
        if isinstance(x[1], dict)
        else MAX_ORDINAL_POSITION,
    )
    
    for col_name, col_info in sorted_cols:
        if isinstance(col_info, dict):
            fields.append({
                "name": col_name,
                "type": col_info.get("data_type", "varchar"),
                "unit": None,
                "nullable": bool(col_info.get("is_nullable", True)),
                "description": None,
                "isAbout": [],
                "valueReference": [],
            })
    
    return fields


def correct_metadata(data: dict, validation_errors: list) -> tuple[dict, str]:
    """Applies corrective logic, fetches table columns dynamically from the OEP API

    for the specified resource path, and integrates them into resource.schema.fields,
    returning the updated dictionary and error code suffix.
    """
    applied_corrections = set()

    # 1. Iterate through resources to fetch and populate schema fields from the OEP API
    if "resources" in data and isinstance(data["resources"], list):
        for resource in data["resources"]:
            path = resource.get("path", "")
            if path and "dataedit/view/" in path:
                table_name = path.split("/")[-1]
                api_url = f"{OEP_API_BASE}/tables/{table_name}/columns/"

                try:
                    response = requests.get(api_url, timeout=DEFAULT_TIMEOUT)
                    response.raise_for_status()
                    api_data = response.json()

                    fields = _extract_fields_from_api_response(api_data)
                    
                    if fields:
                        resource.setdefault("schema", {})
                        resource["schema"]["fields"] = fields
                        applied_corrections.add("FETCH_OEP_COLUMNS")
                        
                except requests.exceptions.RequestException as e:
                    log.error(f"OEP API request failed for {table_name}: {e}")
                except json.JSONDecodeError as e:
                    log.error(f"Invalid JSON response for {table_name}: {e}")

    # 2. Fix root-level 'name' if empty or whitespace-only
    if "name" not in data or not data["name"] or not str(data["name"]).strip():
        if "resources" in data and len(data["resources"]) > 0:
            res_name = data["resources"][0].get("name")
            if res_name and str(res_name).strip():
                data["name"] = res_name
                applied_corrections.add("FIX_EMPTY_NAME_FROM_RESOURCE")
        if not data.get("name"):
            data["name"] = "unnamed-dataset"
            applied_corrections.add("FIX_EMPTY_NAME_DEFAULT")

    # 3. Fix root-level 'title' if empty
    if "title" not in data or not data["title"] or not str(data["title"]).strip():
        if "resources" in data and len(data["resources"]) > 0:
            res_title = data["resources"][0].get("title")
            if res_title and str(res_title).strip():
                data["title"] = res_title
                applied_corrections.add("FIX_EMPTY_TITLE_FROM_RESOURCE")

    # 4. Handle LinkML validation errors (such as metadataVersion)
    for err in validation_errors:
        err_msg = str(err).lower()
        if "required" in err_msg and "metadataversion" in err_msg:
            if "metaMetadata" not in data or not isinstance(data["metaMetadata"], dict):
                data["metaMetadata"] = {}
            data["metaMetadata"]["metadataVersion"] = "2.0.4"
            applied_corrections.add("FIX_METADATA_VERSION")

    # Build error classification code suffix
    if applied_corrections:
        error_code_suffix = f"_corrected_{'_'.join(sorted(applied_corrections))}"
    else:
        error_code_suffix = "_valid_unmodified"

    return data, error_code_suffix


def save_metadata_file(data, file_path: Path):
    """Saves metadata back to its original format."""
    with open(file_path, "w", encoding="utf-8") as f:
        if file_path.suffix.lower() == ".json":
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            yaml.dump(
                data,
                f,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
            )


def process_folder(schema_file: str, input_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    for file_path in input_dir.glob("*.*"):
        if file_path.suffix.lower() not in [".json", ".yaml", ".yml"]:
            continue

        log.info(f"Processing: {file_path.name}")
        data = load_metadata_file(file_path)

        # Validate instance using LinkML's main validator function
        report = validate(data, schema_file)

        errors = []
        if hasattr(report, "results"):
            errors = [r.message for r in report.results]
        elif isinstance(report, list):
            errors = report

        if errors:
            log.info(
                f"  -> Validation failed with {len(errors)} error(s). Applying"
                " corrections..."
            )
            corrected_data, error_code = correct_metadata(data, errors)
        else:
            log.info("  -> Validation passed successfully.")
            corrected_data = data
            error_code = "_valid"

        # Construct new filename with error annotation suffix
        stem = file_path.stem
        suffix = file_path.suffix
        new_filename = f"{stem}{error_code}{suffix}"
        output_file_path = output_dir / new_filename

        save_metadata_file(corrected_data, output_file_path)
        log.info(f"  -> Saved to: {output_file_path}")


if __name__ == "__main__":
    # Example usage
    process_folder(SCHEMA_PATH, RAW_METADATA_DIR, METADATA_DIR)
    # input_file = FILENAME
    # output_file = FILENAME.replace("gathered", "processed")
    # data = process_records(input_file)
    # log.info(f"Successfully processed {len(data)} records.")
#
# # Optional: save to new file
# output_file = Path(RESULT_DIR) / output_file
# with open(output_file, "w", encoding="utf-8") as f:
#     json.dump(data, f, indent=4)
