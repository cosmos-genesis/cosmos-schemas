"""
audit_schema_defaults.py

Checks every Avro schema referenced in schemas/manifest.yml to ensure:

1. If a field type is a union that includes "null", the field MUST specify
   `"default": null`.
2. If a field type does *not* include "null", it MUST NOT specify
   `"default": null` (illegal under Avro spec).

Exit status:
    0 – all schemas pass
    1 – any violation found
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

import yaml

# We are now under schemas/tools/, so the repo root is two levels up.
REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "schemas" / "manifest.yml"


def _load_manifest() -> Dict:
    if not MANIFEST.exists():
        sys.stderr.write(f"Manifest not found at {MANIFEST}\n")
        sys.exit(1)
    return yaml.safe_load(MANIFEST.read_text())


def _iter_schema_files(manifest: Dict) -> List[Path]:
    files: List[Path] = []
    for domain, entries in manifest.get("schemas", {}).items():
        for ent in entries:
            files.append(REPO_ROOT / ent["file"])
    return files


def _is_nullable(avro_type) -> bool:
    if isinstance(avro_type, list):
        return any(
            t == "null" or (isinstance(t, dict) and t.get("type") == "null")
            for t in avro_type
        )
    return False


def _check_schema(path: Path, problems: List[str]) -> None:
    try:
        text = path.read_text()
        schema_json = json.loads(text)
    except Exception as exc:  # pragma: no cover
        problems.append(f"{path}: invalid JSON ({exc})")
        return

    # Schema files may contain a list of definitions
    records = schema_json if isinstance(schema_json, list) else [schema_json]

    for rec in records:
        if rec.get("type") != "record":
            continue

        rec_fullname = f"{rec.get('namespace', '').strip('.')}.{rec['name']}"
        for fld in rec.get("fields", []):
            nullable = _is_nullable(fld["type"])
            has_null_default = "default" in fld and fld["default"] is None

            if nullable and not has_null_default:
                problems.append(
                    f"{rec_fullname}.{fld['name']} – nullable but missing default null"
                )
            if not nullable and has_null_default:
                problems.append(
                    f"{rec_fullname}.{fld['name']} – non-nullable but default null"
                )


def main() -> None:
    manifest = _load_manifest()
    problems: List[str] = []

    for schema_file in _iter_schema_files(manifest):
        if not schema_file.exists():
            problems.append(f"{schema_file} – referenced in manifest but missing")
            continue
        _check_schema(schema_file, problems)

    if problems:
        print("❌ Schema default audit failed:")
        for p in problems:
            print(" •", p)
        sys.exit(1)

    print("✓ All schema defaults are consistent.")
    sys.exit(0)


if __name__ == "__main__":
    main()
