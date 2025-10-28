#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set

import yaml


def load_manifest(manifest_path: Path) -> Dict[str, List[Dict[str, str]]]:
    with manifest_path.open("r", encoding="utf-8") as f:
        content = yaml.safe_load(f)
    if not isinstance(content, dict) or "schemas" not in content:
        raise ValueError(f"Malformed manifest: {manifest_path}")
    schemas = content["schemas"] or {}
    return schemas


def find_avsc_files(root: Path) -> Dict[str, Set[Path]]:
    buckets: Dict[str, Set[Path]] = {}
    for group_dir in root.iterdir():
        if group_dir.is_dir():
            group = group_dir.name
            group_set: Set[Path] = set()
            for p in group_dir.rglob("*.avsc"):
                group_set.add(p.resolve())
            if group_set:
                buckets[group] = group_set
    return buckets


def manifest_entries_to_paths(
    manifest_schemas: Dict[str, List[Dict[str, str]]], project_root: Path
) -> Dict[str, Set[Path]]:
    out: Dict[str, Set[Path]] = {}
    for group, entries in manifest_schemas.items():
        out[group] = set()
        if not entries:
            continue
        for e in entries:
            fp = e.get("file")
            if not fp:
                continue
            out[group].add((project_root / fp).resolve())
    return out


def audit(
    manifest_path: Path, schemas_root: Path
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], Dict[str, List[str]]]:
    fs = find_avsc_files(schemas_root)
    mf = manifest_entries_to_paths(
        load_manifest(manifest_path), project_root=manifest_path.parent.parent
    )

    keep: Dict[str, List[str]] = {}
    remove: Dict[str, List[str]] = {}
    missing: Dict[str, List[str]] = {}

    all_groups = set(fs.keys()) | set(mf.keys())

    for group in sorted(all_groups):
        fs_paths = fs.get(group, set())
        mf_paths = mf.get(group, set())

        keep[group] = sorted(str(p) for p in (fs_paths & mf_paths))
        # present in manifest but not on disk
        remove[group] = sorted(str(p) for p in (mf_paths - fs_paths))
        # present on disk but missing in manifest
        missing[group] = sorted(str(p) for p in (fs_paths - mf_paths))

    return keep, remove, missing


def main():
    parser = argparse.ArgumentParser(
        description="Audit Avro schema manifest vs filesystem."
    )
    parser.add_argument(
        "--manifest", default="schemas/manifest.yml", help="Path to manifest.yml"
    )
    parser.add_argument(
        "--schemas-root", default="schemas", help="Path to schemas root directory"
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    schemas_root = Path(args.schemas_root).resolve()

    keep, remove, missing = audit(manifest_path, schemas_root)

    summary = {
        "keep": keep,
        "remove": remove,
        "missing": missing,
    }

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        for section_name, data in [
            ("KEEP", keep),
            ("REMOVE (in manifest, not on disk)", remove),
            ("MISSING (on disk, not in manifest)", missing),
        ]:
            print(f"\n=== {section_name} ===")
            for group, items in data.items():
                if not items:
                    continue
                print(f"[{group}]")
                for item in items:
                    print(f" - {item}")
        print("\nTip: run with --json for machine-readable output.")

    # return non-zero if any remove or missing to catch drift in CI
    any_issues = any(v for v in remove.values()) or any(v for v in missing.values())
    sys.exit(1 if any_issues else 0)


if __name__ == "__main__":
    main()
