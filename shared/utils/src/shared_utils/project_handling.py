#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Description: Utility to resolve the project root directory based on the location 
             of 'pyproject.toml'.

Author: A. Koubaa
Date: 2026-07-08
"""

from pathlib import Path


def find_project_root() -> Path:
    """
    Returns the project root directory by searching for 'pyproject.toml'.
    Raises FileNotFoundError if the project root cannot be determined.
    """
    # Start searching from the file's own directory
    current_dir = Path(__file__).resolve().parent

    # Check current directory and all parents
    for path in [current_dir, *current_dir.parents]:
        if (path / "pyproject.toml").exists():
            return path

    raise FileNotFoundError(
        "Could not find 'uv.lock'. Are you running this from within the project structure?"
    )

def find_workspace_root() -> Path:
    """Finds the root of the uv workspace by searching upward for the workspace config."""
    current_path = Path(__file__).resolve()

    # Traverse upward through parent directories
    for parent in [current_path] + list(current_path.parents):
        pyproject_path = parent / "pyproject.toml"
        if pyproject_path.exists():
            # Check if it's actually the workspace root containing [tool.uv] with workspace members
            content = pyproject_path.read_text(encoding="utf-8")
            if "[tool.uv]" in content and ("workspace" in content or "members" in content):
                return parent

    raise FileNotFoundError("Could not find the uv workspace root directory.")