#!/usr/bin/env python3
"""
set_avro_versions.py
====================

Ensure every *.avsc has a top-level "version" field.

Priority for version source:
1) If --manifest points to a YAML manifest that includes entries with per-schema
   version values, use those for matching files.
2) Otherwise, use --version provided on the CLI (default: 1.0.0).

Usage:
  python tools/set_avro_versions.py --schemas-dir schemas --manifest schemas/manifest.yml --version 1.0.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional

try:
    import yaml  # type: ignore
except Exception:
    print(
        "ERROR: pyyaml is required to run this tool. Install dependencies with Poetry."
    )
    raise


def load_manifest_versions(manifest_path: Optional[Path]) -> Dict[str, str]:
    """
    Load per-file versions from a YAML manifest, if available.
    Returns a mapping of normalized file path -> version string.
    """
    versions: Dict[str, str] = {}
    if not manifest_path:
        return versions
    if not manifest_path.exists():
        return versions

    try:
        manifest = yaml.safe_load(manifest_path.read_text())
        schemas = manifest.get("schemas", {})
        # Manifest structure: schemas: { category: [ { name, file, version, ...}, ...], ... }
        for category, entries in schemas.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                fpath = entry.get("file")
                ver = entry.get("version")
                if isinstance(fpath, str) and isinstance(ver, (str, int, float)):
                    # Normalize relative POSIX path representation
                    norm = Path(fpath).as_posix()
                    versions[norm] = str(ver)
    except Exception as e:
        print(f"WARNING: Failed to load manifest '{manifest_path}': {e}")
    return versions


def determine_version_for_file(
    avsc_path: Path, manifest_versions: Dict[str, str], default_version: str
) -> str:
    """
    Determine version for a given AVSC file using manifest mapping if present.
    """
    # Try to match by relative path from repo root (posix)
    rel_posix = avsc_path.as_posix()
    # Also try to match by path relative to project root without leading ./ if present
    rel_from_cwd = (
        avsc_path.relative_to(Path(".")).as_posix()
        if avsc_path.is_absolute() is False
        else avsc_path.as_posix()
    )

    # Common manifest "file" entries may be prefixed with "schemas/"
    candidates = {
        rel_posix,
        rel_from_cwd,
        f"schemas/{avsc_path.name}" if "schemas/" not in rel_from_cwd else rel_from_cwd,
        (
            f"schemas/{avsc_path.relative_to('schemas').as_posix()}"
            if rel_from_cwd.startswith("schemas/")
            else rel_from_cwd
        ),
    }

    for key in candidates:
        if key in manifest_versions:
            return manifest_versions[key]

    return default_version


def process_avsc_file(
    avsc_file: Path,
    manifest_versions: Dict[str, str],
    default_version: str,
    dry_run: bool = False,
) -> bool:
    """
    Add a top-level "version" to the AVSC file if missing.
    Returns True if file was modified.
    """
    try:
        raw = avsc_file.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as e:
        print(f"WARNING: Skipping invalid JSON file: {avsc_file} ({e})")
        return False

    if not isinstance(data, dict):
        # Only handle record/enum/fixed schemas represented as dicts
        return False

    if "version" in data and data["version"] not in (None, ""):
        return False  # already has a version

    version_val = determine_version_for_file(
        avsc_file, manifest_versions, default_version
    )
    data["version"] = version_val

    if dry_run:
        print(f"DRY-RUN: would set version={version_val} in {avsc_file}")
        return False

    # Re-write with indentation to keep readable
    avsc_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"✔ Set version={version_val} in {avsc_file}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ensure Avro schemas have a top-level version field."
    )
    parser.add_argument(
        "--schemas-dir",
        type=str,
        default="schemas",
        help="Root directory containing .avsc files (default: schemas)",
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default="schemas/manifest.yml",
        help="Path to manifest.yml (default: schemas/manifest.yml)",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="1.0.0",
        help="Default version to apply when manifest has no entry (default: 1.0.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not modify files; just report actions",
    )
    args = parser.parse_args()

    schemas_root = Path(args.schemas_dir)
    manifest_path = Path(args.manifest) if args.manifest else None
    default_version = args.version

    if not schemas_root.exists():
        print(f"ERROR: schemas directory not found: {schemas_root}")
        sys.exit(2)

    manifest_versions = load_manifest_versions(manifest_path)

    modified = 0
    scanned = 0
    for avsc in schemas_root.rglob("*.avsc"):
        scanned += 1
        if process_avsc_file(
            avsc, manifest_versions, default_version, dry_run=args.dry_run
        ):
            modified += 1

    print(f"\nSummary: scanned {scanned} schema file(s), modified {modified} file(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
