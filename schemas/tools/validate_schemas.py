"""
validate_schemas.py
===================

CLI helper executed via:  poetry run validate-schemas

It checks that:

* schemas/manifest.yml exists and is valid YAML
* every Avro file referenced in the manifest exists and is valid JSON
* the `"version"` field inside each Avro file matches the version stated
  in the manifest entry

Exit status
-----------
0  – all checks pass
1  – any problem found
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

import yaml

# We are now under schemas/tools/, so the repo root is two levels up.
REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "schemas" / "manifest.yml"


class SchemaValidationError(RuntimeError):
    """Raised when the validator detects any mismatch."""


def _load_manifest() -> Dict:
    if not MANIFEST_PATH.exists():
        raise SchemaValidationError("schemas/manifest.yml not found")
    try:
        return yaml.safe_load(MANIFEST_PATH.read_text())
    except yaml.YAMLError as exc:  # pragma: no cover
        raise SchemaValidationError(f"manifest.yml is not valid YAML: {exc}") from exc


def _iter_manifest_entries(manifest: Dict):
    for domain, entries in manifest.get("schemas", {}).items():
        for entry in entries:
            yield domain, entry


def _validate_file(domain: str, entry: Dict, errors: List[str]) -> None:
    avsc_path = REPO_ROOT / entry["file"]
    if not avsc_path.exists():
        errors.append(f"{domain}.{entry['name']}: file missing at {avsc_path}")
        return

    try:
        schema_json = json.loads(avsc_path.read_text())
    except json.JSONDecodeError as exc:
        errors.append(f"{avsc_path}: invalid JSON ({exc})")
        return

    # Allow files that contain a list of definitions
    top = schema_json[0] if isinstance(schema_json, list) else schema_json
    embedded_version = top.get("version")
    declared_version = entry.get("version")
    if embedded_version != declared_version:
        errors.append(
            f"{domain}.{entry['name']}: version mismatch "
            f"(manifest={declared_version}, file={embedded_version})"
        )


def validate() -> List[str]:
    manifest = _load_manifest()
    problems: List[str] = []
    for domain, entry in _iter_manifest_entries(manifest):
        _validate_file(domain, entry, problems)
    return problems


def main() -> None:
    issues = validate()
    if issues:
        print("❌ Schema validation failed:")
        for issue in issues:
            print(" •", issue)
        sys.exit(1)

    print("✓ Schema manifest and Avro files are consistent.")
    sys.exit(0)


if __name__ == "__main__":
    main()
