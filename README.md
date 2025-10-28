# Cosmos Genesis™ Schemas

**Open-source schema definitions for Universe-as-a-Service**

[![Schema Count](https://img.shields.io/badge/schemas-89-blue)](schemas/manifest.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Website](https://img.shields.io/badge/website-cosmosgenesis.com-cyan)](https://cosmosgenesis.com)

## Overview

This repository contains **89 open-source Avro schema definitions** for astrophysical objects and phenomena used in the Cosmos Genesis platform. These schemas enable researchers, game developers, and space simulation enthusiasts to work with scientifically-validated universe data at trillion-object scale.

## What's Inside

### Schema Categories

- **Celestial Objects** (19 schemas): Stars, planets, moons, asteroids, comets
- **Cosmic Phenomena** (16 schemas): Black holes, nebulae, protoplanetary disks, supernovae
- **Physics Models** (8 schemas): Stellar evolution, orbital mechanics, gravitational interactions
- **Environmental** (12 schemas): Atmospheres, magnetic fields, radiation belts
- **System Schemas** (11 schemas): Star systems, galaxies, clusters
- **Biological** (6 schemas): Habitability models, biosignatures
- **Properties** (9 schemas): Physical constants, material compositions
- **Temporal** (8 schemas): Time evolution, aging dynamics

**Total: 89 schemas** | [Browse Full Manifest →](schemas/manifest.yml)

## Quick Start

### For Researchers

```bash
# Clone the repository
git clone https://github.com/cosmosgenesis/cosmos-schemas.git
cd cosmos-schemas

# Explore schema definitions
cat schemas/manifest.yml
cat schemas/celestial_objects/StarSchema.avsc
```

### For Developers

```python
# Install Python SDK (coming soon)
pip install cosmos-genesis-client

# Query universe data
from cosmos_genesis import CosmosClient

client = CosmosClient(api_key="your_api_key")
stars = client.query("SELECT * FROM star WHERE stellar_mass_msun > 10")
```

## Schema Documentation

**[📖 Interactive Schema Browser](https://cosmosgenesis.github.io/cosmos-schemas/)** (GitHub Pages)

Browse all 89 schemas with:
- Field definitions and types
- Physics metadata (evolution models, timescales)
- Relationships between schemas
- Example queries

## Scientific Validation

All schemas implement peer-reviewed astrophysics models:

- **Stellar Evolution**: Hurley et al. (2000) Single Star Evolution
- **Initial Mass Function**: Kroupa (2001) IMF
- **Galactic Structure**: Bovy (2017) density distributions
- **Planetary Formation**: Hansen & Murray (2012) migration models

**[Read Research Whitepaper →](https://cosmosgenesis.com/#whitepapers)**

## Repository Structure

```
cosmos-schemas/
├── schemas/               # 89 Avro schema definitions
│   ├── manifest.yml      # Master schema catalog
│   ├── celestial_objects/
│   ├── cosmic_phenomena/
│   ├── physics/
│   └── ...
├── docs/
│   └── schema-browser/   # Auto-generated HTML documentation
├── tools/
│   ├── validate_schema.py
│   └── generate_docs.py
└── examples/
    └── sample-data/      # Small sample datasets
```

## Usage Examples

### Querying Star Data

```sql
-- Find massive O-type stars
SELECT
  system_id,
  stellar_mass_msun,
  luminosity_lsun,
  age_myr
FROM star
WHERE
  spectral_type = 'O'
  AND stellar_mass_msun > 20
LIMIT 100;
```

### Analyzing Exoplanet Populations

```sql
-- Rocky planets in habitable zone
SELECT
  planet_id,
  mass_earth,
  semi_major_axis_au,
  equilibrium_temperature_k
FROM planet
WHERE
  planet_type = 'ROCKY'
  AND semi_major_axis_au BETWEEN 0.95 AND 1.37  -- Sun-like star HZ
  AND mass_earth BETWEEN 0.5 AND 5.0;
```

## API Access

Cosmos Genesis provides **cloud-native API access** to trillion-object universe datasets:

- **No HPC required** - Query from any machine with AWS credentials
- **SQL interface** - Standard Athena queries via boto3
- **Reproducible experiments** - Deterministic seeding with `galaxy_id`
- **Academic pricing** - $500/month for 10M+ star systems

**[Apply for Research Access →](https://cosmosgenesis.com/#beta-signup)**

## Pricing

| Tier | Monthly | Scale | Target |
|------|---------|-------|--------|
| **Academic** | $500 | 10M systems | Researchers with .edu email |
| **Creator** | $300 | 10M systems | Indie developers, small studios |
| **Studio** | $2,500 | 100M systems | Mid-size studios, research labs |
| **Franchise** | Custom | 10B+ objects | AAA studios, space agencies |

**First 50 customers: 20% lifetime discount**

## Contributing

Schema improvements welcome! Please:

1. Fork this repository
2. Make changes to schema `.avsc` files
3. Run `python tools/validate_schema.py`
4. Submit pull request with rationale

**Note:** These schemas are **derived from** our private production system. Complex changes may require coordination with the core team.

## Citation

If you use Cosmos Genesis data in research, please cite:

```bibtex
@software{cosmosgenesis2025,
  author = {Edwards, Shawn},
  title = {Cosmos Genesis: Universe-as-a-Service},
  year = {2025},
  url = {https://github.com/cosmosgenesis/cosmos-schemas},
  doi = {10.5281/zenodo.XXXXXXX}
}
```

## License

**Apache License 2.0** - See [LICENSE](LICENSE) for details.

Schema definitions are open-source. The Cosmos Genesis platform and generation algorithms remain proprietary.

## Links

- **Website**: [cosmosgenesis.com](https://cosmosgenesis.com)
- **Interactive Demo**: [demo.cosmosgenesis.com](https://demo.cosmosgenesis.com)
- **Python SDK**: [cosmos-python-sdk](https://github.com/cosmosgenesis/cosmos-python-sdk) (coming soon)
- **Documentation**: [docs.cosmosgenesis.com](https://docs.cosmosgenesis.com) (coming soon)

## Contact

- **Email**: info@cosmosgenesis.com
- **Research Inquiries**: founder@cosmosgenesis.com
- **Issues**: [GitHub Issues](https://github.com/cosmosgenesis/cosmos-schemas/issues)

---

**Cosmos Genesis™** - *We build the universe. You build the worlds.™*
