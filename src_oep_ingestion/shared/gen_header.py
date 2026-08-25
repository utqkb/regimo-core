#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_header.py

Generate a standard Python file header (shebang, encoding declaration,
module docstring with author/affiliation/license, creation date) and
either print it or prepend it to a target file.

Author: A. Koubaa
Affiliation: Karlsruhe Institute of Technology (KIT)
License: MIT
Created: 2026-07-08
"""

import argparse
import datetime
import pathlib

AUTHOR = "A. Koubaa"
AFFILIATION = "Karlsruhe Institute of Technology (KIT)"
LICENSE = "MIT"


def build_header(module_name: str, description: str) -> str:
    today = datetime.date.today().isoformat()
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{module_name}

{description}

Author: {AUTHOR}
Affiliation: {AFFILIATION}
License: {LICENSE}
Created: {today}
"""

from shared_utils.logging_config import get_logger

# === CONFIGURATION & LOGGER ==============================================
from config.oep_config import BASE_URL, SCHEMA
from config.neo_config import URI, USER, PASSWORD
log = get_logger("{module_name}")

'''


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a standard Python file header."
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="Path to a .py file. If it exists, header is prepended "
             "(unless it already starts with a shebang). If it doesn't "
             "exist, it is created with the header. If omitted, the "
             "header is printed to stdout.",
    )
    parser.add_argument(
        "-m", "--module-name",
        default=None,
        help="Module name for the docstring title (default: derived "
             "from the target filename, or 'module' if none given).",
    )
    parser.add_argument(
        "-d", "--description",
        default="TODO: one-line description of this module.",
        help="Short description sentence for the docstring.",
    )
    args = parser.parse_args()

    if args.target:
        path = pathlib.Path(args.target)
        module_name = args.module_name or path.stem
    else:
        path = None
        module_name = args.module_name or "module"

    header = build_header(module_name, args.description)

    if path is None:
        print(header, end="")
        return

    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing.startswith("#!"):
            print(f"Skipped: {path} already starts with a shebang/header.")
            return
        path.write_text(header + existing, encoding="utf-8")
        print(f"Prepended header to existing file: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(header, encoding="utf-8")
        print(f"Created new file with header: {path}")


if __name__ == "__main__":
    main()