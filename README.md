# 📦 CosmosGenesis – Unified Avro Schema Repository

This directory is **the single source of truth** for every Avro schema that feeds
our data-lake and real-time processing pipelines.

## Naming policy and aliasing

To keep references stable across teams and code generators:

- Canonical schema names are unsuffixed (e.g., MagneticField).
- Every schema is aliased with both the unsuffixed and Schema-suffixed forms (e.g., MagneticField and MagneticFieldSchema).
- The manifest encodes this policy so that generators can accept either form and resolve to the canonical name.

Normalize and update the manifest to include all schemas and aliases:
- Dry run (report only): python -m schemas.tools.normalize_manifest
- Write changes: python -m schemas.tools.normalize_manifest --write

Generator defaults:
- Generators should default schema_name to the unsuffixed canonical name.
- If a Schema-suffixed name is provided, rely on manifest aliasing for resolution (no special-casing in generators).

## Why a new location?

* `services/galaxy_generator/schemas/**` was only meant for demo data-generation
  and has already drifted from production needs.
* Multiple helper classes hard-coded inconsistent search paths, making automatic
  pipeline generation brittle.
* A clearly-defined structure under the project root keeps the contract with
  downstream consumers (Spark, Glue, Flink, Athena, Redshift Spectrum, …)
  stable even as micro-services evolve.

## Directory layout
