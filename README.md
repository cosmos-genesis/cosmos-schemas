# Cosmos Genesis Schemas

**89 open-source Avro schemas for astrophysical simulation data**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Schema Browser](https://img.shields.io/badge/docs-schema%20browser-green)](https://cosmos-genesis.github.io/cosmos-schemas/)

Cosmos Genesis Schemas provides production-ready data schemas for building universe-scale simulations, spacefaring games, and astrophysical research applications.

## What's Included

### 🌌 Galactic & Cosmic Structures
- Galaxies, star clusters, nebulae, protoplanetary disks
- Black holes, dark matter halos, cosmic filaments

### ⭐ Stellar Objects
- Stars with full stellar evolution parameters
- Binary and multiple star systems
- Stellar populations and initial mass functions

### 🪐 Planetary Systems
- Planets, moons, asteroid belts, Oort clouds
- Planetary rings, atmospheres, magnetic fields
- Orbital mechanics and Keplerian elements

### ⚛️ Physics & Evolution
- Stellar evolution (main sequence, giants, supernovae)
- Atmospheric composition and chemistry
- Temporal snapshots for universe aging

### 🔬 Scientific Validation
All schemas implement peer-reviewed astrophysical models:
- **Stellar masses**: Kroupa (2001) Initial Mass Function
- **Stellar evolution**: Hurley et al. (2000) Single Stellar Evolution
- **Atmospheric models**: Gas giant and terrestrial composition

## Quick Start

### Browse the Schemas
Explore all 89 schemas interactively:
**[📖 Interactive Schema Browser](https://cosmos-genesis.github.io/cosmos-schemas/)**

### Query Data with Python
Use the [Cosmos Python SDK](https://github.com/cosmos-genesis/cosmos-python-sdk) to query universe data:

```python
from cosmos_genesis import CosmosClient

client = CosmosClient(api_key="your-key")
results = client.query_galaxy(
    galaxy_id="spiral-sm-2arm-001",
    query="SELECT * FROM star WHERE stellar_mass_msun > 10 LIMIT 100"
)
```

## Use Cases

### 🎮 Game Development
- Elite Dangerous-style space exploration
- Procedural universe generation with scientific accuracy
- Persistent universe infrastructure for multiplayer games

### 🎬 Film & VFX
- Scientifically-accurate space scenes
- Consistent universe data across projects
- Real stellar evolution for time-lapse sequences

### 🔭 Research & Education
- Statistical studies of galactic populations
- Educational simulations with validated physics
- Reproducible astrophysical experiments

## Schema Categories

| Category | Count | Examples |
|----------|-------|----------|
| **Celestial** | 15 | Star, Planet, Moon, Asteroid |
| **Cosmic** | 8 | Galaxy, Nebula, BlackHole, DarkMatterHalo |
| **Galactic** | 12 | SpiralArm, StarCluster, GalacticDisk |
| **Orbital** | 9 | OrbitalElements, TidalForces, OortCloud |
| **Stellar** | 11 | StellarWind, Supernova, BinarySystem |
| **Environmental** | 14 | Atmosphere, MagneticField, Radiation |
| **Temporal** | 5 | UniverseTime, Snapshot, EvolutionHistory |
| **Physics** | 15 | StellarEvolution, AtmosphericChemistry |

See [manifest.yml](schemas/manifest.yml) for the complete catalog.

## Schema Format

All schemas are defined in [Apache Avro](https://avro.apache.org/) format:

```json
{
  "type": "record",
  "name": "Star",
  "namespace": "com.cosmosgenesis.schemas.celestial",
  "fields": [
    {"name": "star_id", "type": "string"},
    {"name": "stellar_mass_msun", "type": "double"},
    {"name": "stellar_type", "type": "string"},
    {"name": "age_myr", "type": "double"}
  ]
}
```

## Installation

### Clone the Repository
```bash
git clone https://github.com/cosmos-genesis/cosmos-schemas.git
cd cosmos-schemas
```

### Validate Schemas
```bash
python -m schemas.tools.validate_table_names
python -m schemas.tools.audit_schema_defaults
```

### Normalize Manifest
```bash
# Dry run (report only)
python -m schemas.tools.normalize_manifest

# Write changes
python -m schemas.tools.normalize_manifest --write
```

## Documentation

- **[Schema Browser](https://cosmos-genesis.github.io/cosmos-schemas/)** - Interactive documentation
- **[Python SDK](https://github.com/cosmos-genesis/cosmos-python-sdk)** - Query interface and examples
- **[manifest.yml](schemas/manifest.yml)** - Complete schema catalog with physics metadata

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/new-schema`)
3. Add your schema in the appropriate category directory
4. Update `manifest.yml` with schema metadata
5. Run validation: `python -m schemas.tools.validate_table_names`
6. Submit a pull request

### Schema Contribution Guidelines

- Use descriptive field names with units (e.g., `mass_msun` for solar masses)
- Include `"default": null` for all optional fields
- Follow naming conventions: PascalCase for schema names, snake_case for fields
- Add physics metadata to manifest (evolution model, timescale, priority)

## License

This project is licensed under the **Apache License 2.0** - see [LICENSE](LICENSE) for details.

## Citation

If you use these schemas in academic work, please cite:

```bibtex
@software{cosmos_schemas_2025,
  title = {Cosmos Genesis Schemas: Astrophysical Data Schemas for Universe-Scale Simulations},
  author = {Cosmos Genesis},
  year = {2025},
  url = {https://github.com/cosmos-genesis/cosmos-schemas}
}
```

## Links

- **Website**: [cosmosgenesis.com](https://cosmosgenesis.com)
- **Demo**: [demo.cosmosgenesis.com](https://demo.cosmosgenesis.com)
- **Python SDK**: [github.com/cosmos-genesis/cosmos-python-sdk](https://github.com/cosmos-genesis/cosmos-python-sdk)
- **Schema Browser**: [cosmos-genesis.github.io/cosmos-schemas](https://cosmos-genesis.github.io/cosmos-schemas/)

---

**Built with scientific rigor. Designed for universe-scale applications.**
