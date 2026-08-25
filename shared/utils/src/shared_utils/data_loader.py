#!/usr/bin/env python3
"""
Common data loading utilities for TF Harmony analysis.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_json_results(file_path: str) -> Optional[Dict[str, Any]]:
    """Load analysis results from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def save_json_results(data: Dict[str, Any], file_path: str) -> bool:
    """Save analysis results to JSON file."""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving to {file_path}: {e}")
        return False

def save_csv_report(data: List[Dict[str, Any]], file_path: str, fieldnames: List[str] = None) -> bool:
    """Save analysis results to CSV file."""
    if not data:
        return False
        
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        if fieldnames is None:
            fieldnames = list(data[0].keys())
            
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error saving CSV to {file_path}: {e}")
        return False

