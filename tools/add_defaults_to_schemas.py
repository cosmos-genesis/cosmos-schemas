#!/usr/bin/env python3
"""
add_defaults_to_schemas.py
--------------------------

Walk every *.avsc file beneath the ./schemas directory and ensure all
fields have Avro-compliant default values.

Usage:
    python tools/add_defaults_to_schemas.py   # modifies files in-place
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Union

# We are now under schemas/tools/, so SCHEMA_ROOT is one level up.
SCHEMA_ROOT = Path(__file__).resolve().parents[1]


Primitive = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


def _default_for_type(avro_type: Primitive) -> Primitive:
    """
    Return an appropriate default value for the given Avro *type*.
    The argument can be:
      • a primitive string ("string", "double", …)
      • a union (list)
      • a complex type (dict)
    """
    # Primitive type expressed as a string
    if isinstance(avro_type, str):
        return {
            "string": "",
            "bytes": "",
            "boolean": False,
            "int": 0,
            "long": 0,
            "float": 0.0,
            "double": 0.0,
        }.get(avro_type, None)

    # Union of types
    if isinstance(avro_type, list):
        # If union contains "null" as first branch → null is legal default.
        if avro_type and avro_type[0] == "null":
            return None
        # Else default should come from first branch.
        return _default_for_type(avro_type[0])

    # Complex dict
    if isinstance(avro_type, dict):
        avro_type_name = avro_type.get("type")
        if avro_type_name == "array":
            return []
        if avro_type_name == "map":
            return {}
        if avro_type_name == "enum":
            symbols = avro_type.get("symbols", [])
            return symbols[0] if symbols else ""
        if avro_type_name == "fixed":
            # fall back to empty bytes
            return ""
        if avro_type_name == "record":
            # For nested records a default is usually a dict of field defaults,
            # but supplying an empty dict is safest/backward compatible.
            return {}
        # Unknown complex type
        return None

    # Fallback
    return None


def _inject_defaults(schema: Dict[str, Any]) -> bool:
    """
    Recursively walk `schema` and inject defaults where missing.

    Returns True if the schema dict was modified.
    """
    modified = False
    if "fields" not in schema:
        return modified

    for field in schema["fields"]:
        if "default" not in field:
            default_value = _default_for_type(field["type"])
            if default_value is not None:
                field["default"] = default_value
                modified = True

        # Recurse into nested records / arrays
        field_type = field["type"]
        # List ⇒ union
        if isinstance(field_type, list):
            for branch in field_type:
                if isinstance(branch, dict):
                    modified |= _inject_defaults(branch)
        # Dict ⇒ complex type
        if isinstance(field_type, dict):
            t = field_type.get("type")
            if t == "array":
                items = field_type.get("items")
                if isinstance(items, dict):
                    modified |= _inject_defaults(items)
            elif t == "map":
                values = field_type.get("values")
                if isinstance(values, dict):
                    modified |= _inject_defaults(values)
            elif t == "record":
                modified |= _inject_defaults(field_type)
            # enum / fixed do not contain fields

    return modified


def process_file(path: Path) -> bool:
    text = path.read_text()
    data = json.loads(text)
    changed = _inject_defaults(data)
    if changed:
        path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n")
    return changed


def main() -> None:
    if not SCHEMA_ROOT.exists():
        print(f"Schema directory {SCHEMA_ROOT} not found", file=sys.stderr)
        sys.exit(1)

    avsc_files = list(SCHEMA_ROOT.rglob("*.avsc"))
    if not avsc_files:
        print("No .avsc files found.", file=sys.stderr)
        sys.exit(1)

    total_changed = 0
    for avsc in avsc_files:
        if process_file(avsc):
            total_changed += 1
            print(f"✔  Updated defaults in {avsc.relative_to(Path.cwd())}")

    if total_changed == 0:
        print("All schemas already contain appropriate defaults ✅")
    else:
        print(f"Completed. {total_changed} schema(s) modified.")


if __name__ == "__main__":
    main()
