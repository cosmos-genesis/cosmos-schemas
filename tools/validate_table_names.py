#!/usr/bin/env python3
"""
validate_table_names.py
=======================

Validates that all schemas in manifest.yml have explicit table_name field.
This ensures the manifest is the single source of truth for table naming.

Exit status:
0  – all checks pass
1  – any problem found

Usage:
    python -m schemas.tools.validate_table_names
    python schemas/tools/validate_table_names.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

import yaml

# Repo root is two levels up from this file
REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "schemas" / "manifest.yml"


def validate_table_names() -> List[str]:
    """
    Validate that all schemas in manifest have explicit table_name field.

    Returns
    -------
    List[str]
        List of error messages. Empty list means validation passed.
    """
    if not MANIFEST_PATH.exists():
        return [f"manifest.yml not found at {MANIFEST_PATH}"]

    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        return [f"manifest.yml is not valid YAML: {exc}"]

    errors: List[str] = []
    total_schemas = 0
    schemas_with_table_name = 0
    duplicate_table_names: Dict[str, List[str]] = {}

    # Check each schema in manifest
    for category, entries in manifest.get("schemas", {}).items():
        if not isinstance(entries, list):
            continue

        for entry in entries:
            if not isinstance(entry, dict):
                continue

            total_schemas += 1
            name = entry.get("name", "")
            table_name = entry.get("table_name")

            if not name:
                errors.append(f"{category}: schema entry missing 'name' field")
                continue

            if not table_name:
                errors.append(
                    f"{category}.{name}: missing 'table_name' field. "
                    "All schemas must have explicit table_name for consistency."
                )
            else:
                schemas_with_table_name += 1

                # Check for duplicate table names
                if table_name not in duplicate_table_names:
                    duplicate_table_names[table_name] = []
                duplicate_table_names[table_name].append(f"{category}.{name}")

    # Check for duplicates
    for table_name, schema_list in duplicate_table_names.items():
        if len(schema_list) > 1:
            errors.append(
                f"Duplicate table_name '{table_name}' used by: {', '.join(schema_list)}"
            )

    # Summary
    print("\nTable Name Validation Report:")
    print(f"  Total schemas: {total_schemas}")
    print(f"  Schemas with table_name: {schemas_with_table_name}")
    print(f"  Schemas missing table_name: {total_schemas - schemas_with_table_name}")

    return errors


def main() -> None:
    issues = validate_table_names()

    if issues:
        print("\n❌ Table name validation failed:")
        for issue in issues:
            print(f" •  {issue}")
        sys.exit(1)

    print("✓ All schemas have explicit table_name field. Naming is consistent!")
    sys.exit(0)


if __name__ == "__main__":
    main()
