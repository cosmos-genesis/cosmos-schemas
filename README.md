# 📦 CosmosGenesis – Unified Avro Schema Repository

This directory is **the single source of truth** for every Avro schema that feeds
our data-lake and real-time processing pipelines.

## Why a new location?

* `services/galaxy_generator/schemas/**` was only meant for demo data-generation
  and has already drifted from production needs.
* Multiple helper classes hard-coded inconsistent search paths, making automatic
  pipeline generation brittle.
* A clearly-defined structure under the project root keeps the contract with
  downstream consumers (Spark, Glue, Flink, Athena, Redshift Spectrum, …)
  stable even as micro-services evolve.

## Directory layout
