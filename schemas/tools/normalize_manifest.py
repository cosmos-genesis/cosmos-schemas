#!/usr/bin/env python3
"""
normalize_manifest.py

Scans schemas/**/*.avsc and ensures schemas/manifest.yml:
 - includes every schema file grouped by its top-level folder
 - uses a consistent canonical name (unsuffixed by default)
 - provides aliases for both unsuffixed and Schema-suffixed names
 - preserves existing description/compatibility/version when present

Usage:
  Dry run (report only):
    python -m schemas.tools.normalize_manifest
  Write changes to manifest:
    python -m schemas.tools.normalize_manifest --write
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_ROOT = REPO_ROOT / "schemas"
MANIFEST_PATH = SCHEMAS_ROOT / "manifest.yml"


@dataclass
class AvroRecordInfo:
    group: str
    file_rel: str
    name: str
    namespace: str
    doc: Optional[str]


def _read_manifest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"version": 1, "schemas": {}}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "schemas" not in data:
        data["schemas"] = {}
    # ensure naming policy exists
    naming = data.get("naming") or {}
    if "canonical" not in naming:
        naming["canonical"] = "unsuffixed"
    if "alias_patterns" not in naming:
        naming["alias_patterns"] = ["{name}", "{name}Schema"]
    data["naming"] = naming
    return data


def _iter_avsc_files(root: Path) -> List[Path]:
    skip = {"tools", "__pycache__"}
    out: List[Path] = []
    for child in root.iterdir():
        if not child.is_dir() or child.name in skip:
            continue
        for p in child.rglob("*.avsc"):
            out.append(p)
    return out


def _pick_primary_record(schema_json: Any, file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Avro files might contain a single record or a list of definitions.
    Prefer a record whose name matches the filename (with or without 'Schema').
    Otherwise take the first record found.
    """
    candidates: List[Dict[str, Any]] = []
    if isinstance(schema_json, dict):
        if schema_json.get("type") == "record":
            candidates.append(schema_json)
    elif isinstance(schema_json, list):
        for item in schema_json:
            if isinstance(item, dict) and item.get("type") == "record":
                candidates.append(item)
    if not candidates:
        return None

    stem = file_path.stem  # e.g., MagneticFieldSchema
    preferred = [
        r
        for r in candidates
        if r.get("name") == stem or r.get("name") == stem.replace("Schema", "")
    ]
    return preferred[0] if preferred else candidates[0]


def _scan_avro() -> List[AvroRecordInfo]:
    records: List[AvroRecordInfo] = []
    for avsc_path in _iter_avsc_files(SCHEMAS_ROOT):
        try:
            data = json.loads(avsc_path.read_text(encoding="utf-8"))
        except Exception:
            # skip invalid JSON; separate validators will catch this
            continue

        rec = _pick_primary_record(data, avsc_path)
        if not rec or rec.get("type") != "record":
            continue

        group = avsc_path.relative_to(SCHEMAS_ROOT).parts[0]
        file_rel = str(avsc_path.relative_to(REPO_ROOT)).replace("\\", "/")
        name = rec.get("name")
        namespace = rec.get("namespace", "")
        doc = rec.get("doc")
        records.append(
            AvroRecordInfo(
                group=group, file_rel=file_rel, name=name, namespace=namespace, doc=doc
            )
        )
    return records


def _canonicalize_name(name: str, canonical_style: str = "unsuffixed") -> str:
    if canonical_style == "unsuffixed":
        return name[:-6] if name.endswith("Schema") else name
    # future styles can be added here
    return name


def _derive_table_name(name: str, canonical_style: str = "unsuffixed") -> str:
    """
    Derive lowercase table name from schema name.

    Examples:
        "Star" -> "star"
        "StarSchema" -> "star"
        "ProtoplanetaryDisk" -> "protoplanetarydisk"
    """
    canonical = _canonicalize_name(name, canonical_style)
    # Remove "Schema" suffix if present, then lowercase
    base = canonical[:-6] if canonical.endswith("Schema") else canonical
    return base.lower()


def _aliases_for(name: str, canonical_style: str = "unsuffixed") -> List[str]:
    base = _canonicalize_name(name, canonical_style)
    alts = {base, f"{base}Schema", name}
    # ensure deterministic order with canonical first
    rest = sorted(x for x in alts if x != base)
    return [base] + rest


def _entry_key(entry: Dict[str, Any]) -> Tuple[str, str]:
    # Key by file path to avoid duplicates
    return (entry.get("file", ""), entry.get("namespace", ""))


def _merge_manifest(
    existing: Dict[str, Any], scans: List[AvroRecordInfo]
) -> Dict[str, Any]:
    canonical_style = (existing.get("naming") or {}).get("canonical", "unsuffixed")

    # Build quick lookup from existing entries by (file, namespace)
    existing_by_group: Dict[str, Dict[Tuple[str, str], Dict[str, Any]]] = {}
    for group, entries in (existing.get("schemas") or {}).items():
        group_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for e in entries or []:
            group_map[_entry_key(e)] = e
        existing_by_group[group] = group_map

    # Merge or add entries
    out_schemas: Dict[str, List[Dict[str, Any]]] = {}
    for info in scans:
        group_entries = out_schemas.setdefault(info.group, [])
        entry_key = (info.file_rel, info.namespace)
        existing_entry = existing_by_group.get(info.group, {}).get(entry_key)

        canonical_name = _canonicalize_name(info.name, canonical_style)
        alias_list = _aliases_for(info.name, canonical_style)
        table_name = _derive_table_name(info.name, canonical_style)

        if existing_entry:
            # Preserve description/compatibility/version if present
            desc = existing_entry.get("description") or info.doc
            comp = existing_entry.get("compatibility") or "BACKWARD"
            ver = existing_entry.get("version") or "1.0.0"
            # CRITICAL: Preserve physics metadata, primary_key, and table_name
            primary_key = existing_entry.get("primary_key")
            physics = existing_entry.get("physics")
            # Use existing table_name if present, otherwise derive
            table_name = existing_entry.get("table_name") or table_name
        else:
            desc = info.doc
            comp = "BACKWARD"
            ver = "1.0.0"
            primary_key = None
            physics = None

        merged = {
            "name": canonical_name,
            "aliases": alias_list,
            "file": info.file_rel,
            "namespace": info.namespace,
            "description": desc,
            "compatibility": comp,
            "version": ver,
            "table_name": table_name,  # ALWAYS include table_name
        }

        # Add optional fields only if they exist (maintain clean YAML)
        if primary_key:
            merged["primary_key"] = primary_key
        if physics:
            merged["physics"] = physics

        group_entries.append(merged)

    # Include any existing entries that reference files no longer present (so we don't drop them silently)
    for group, entries in (existing.get("schemas") or {}).items():
        for e in entries or []:
            key = _entry_key(e)
            # If not already added from scans, keep as-is
            if group not in out_schemas or all(
                _entry_key(x) != key for x in out_schemas[group]
            ):
                out = dict(e)
                # Normalize aliases, name, and table_name if missing
                if "name" in out:
                    out.setdefault(
                        "aliases", _aliases_for(out["name"], canonical_style)
                    )
                    out["name"] = _canonicalize_name(out["name"], canonical_style)
                    # Add table_name if missing
                    if "table_name" not in out:
                        out["table_name"] = _derive_table_name(
                            out["name"], canonical_style
                        )
                out_schemas.setdefault(group, []).append(out)

    # Sort deterministically
    for group in out_schemas:
        out_schemas[group].sort(
            key=lambda e: (e.get("namespace", ""), e.get("name", ""), e.get("file", ""))
        )

    new_manifest = {
        "version": existing.get("version", 1),
        "naming": existing.get(
            "naming",
            {
                "canonical": canonical_style,
                "alias_patterns": ["{name}", "{name}Schema"],
            },
        ),
        "schemas": out_schemas,
    }
    return new_manifest


def main() -> None:
    global SCHEMAS_ROOT

    parser = argparse.ArgumentParser(
        description="Normalize schemas/manifest.yml to include all schemas and consistent aliases."
    )
    parser.add_argument(
        "--manifest", default=str(MANIFEST_PATH), help="Path to manifest.yml"
    )
    parser.add_argument(
        "--schemas-root",
        default=str(SCHEMAS_ROOT),
        help="Path to schemas root directory",
    )
    parser.add_argument(
        "--write", action="store_true", help="Write changes back to manifest.yml"
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    # Allow scanning different root if requested
    SCHEMAS_ROOT = Path(args.schemas_root).resolve()

    existing = _read_manifest(manifest_path)
    scans = _scan_avro()
    new_manifest = _merge_manifest(existing, scans)

    # Simple change detection
    existing_yaml = yaml.safe_dump(
        existing, sort_keys=False, allow_unicode=True
    ).strip()
    new_yaml = yaml.safe_dump(new_manifest, sort_keys=False, allow_unicode=True).strip()

    if existing_yaml == new_yaml:
        print("✓ Manifest is already normalized. No changes needed.")
        return

    if args.write:
        yaml_text = yaml.safe_dump(new_manifest, sort_keys=False, allow_unicode=True)
        manifest_path.write_text(yaml_text, encoding="utf-8")
        print(f"✓ Wrote normalized manifest to {manifest_path}")
    else:
        print("Manifest would be updated. Run with --write to apply changes.")
        # provide a short diff-like summary
        old_groups = set((existing.get("schemas") or {}).keys())
        new_groups = set((new_manifest.get("schemas") or {}).keys())
        added_groups = sorted(new_groups - old_groups)
        removed_groups = sorted(old_groups - new_groups)
        if added_groups:
            print(" + groups:", ", ".join(added_groups))
        if removed_groups:
            print(" - groups:", ", ".join(removed_groups))
        # counts per group
        for grp in sorted(new_groups | old_groups):
            old_cnt = len((existing.get("schemas") or {}).get(grp, []) or [])
            new_cnt = len((new_manifest.get("schemas") or {}).get(grp, []) or [])
            if old_cnt != new_cnt:
                print(f" * {grp}: {old_cnt} -> {new_cnt} entries")


if __name__ == "__main__":
    main()
