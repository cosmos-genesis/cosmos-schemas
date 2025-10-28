#!/usr/bin/env python3
"""
Generate static HTML schema documentation from manifest.yml
Creates a GitHub Pages-ready schema browser
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any

def load_manifest() -> Dict:
    """Load schemas/manifest.yml"""
    manifest_path = Path(__file__).parent.parent / "schemas" / "manifest.yml"
    with open(manifest_path) as f:
        return yaml.safe_load(f)

def load_avro_schema(schema_path: Path) -> Dict:
    """Load individual Avro schema file"""
    with open(schema_path) as f:
        return json.load(f)

def generate_index_html(manifest: Dict, output_dir: Path):
    """Generate main index page with schema categories"""

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cosmos Genesis Schema Browser</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            line-height: 1.6;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        header {
            text-align: center;
            padding: 3rem 0;
            border-bottom: 2px solid #334155;
        }
        h1 {
            font-size: 3rem;
            background: linear-gradient(135deg, #60a5fa 0%, #34d399 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        .subtitle { color: #94a3b8; font-size: 1.2rem; }
        .stats {
            display: flex;
            gap: 2rem;
            justify-content: center;
            margin: 2rem 0;
            flex-wrap: wrap;
        }
        .stat-card {
            background: #1e293b;
            padding: 1rem 2rem;
            border-radius: 8px;
            border: 1px solid #334155;
        }
        .stat-number { font-size: 2rem; font-weight: bold; color: #60a5fa; }
        .stat-label { color: #94a3b8; font-size: 0.9rem; }
        .categories {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 3rem 0;
        }
        .category-card {
            background: #1e293b;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #334155;
            transition: all 0.3s;
        }
        .category-card:hover {
            border-color: #60a5fa;
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(96, 165, 250, 0.2);
        }
        .category-title {
            font-size: 1.5rem;
            color: #60a5fa;
            margin-bottom: 0.5rem;
        }
        .category-count {
            color: #94a3b8;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        .schema-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .schema-list li a {
            color: #cbd5e1;
            text-decoration: none;
            padding: 0.5rem;
            display: block;
            border-radius: 4px;
            transition: background 0.2s;
        }
        .schema-list li a:hover {
            background: #334155;
            color: #60a5fa;
        }
        footer {
            text-align: center;
            padding: 2rem;
            margin-top: 4rem;
            border-top: 2px solid #334155;
            color: #64748b;
        }
        footer a { color: #60a5fa; text-decoration: none; }
        footer a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Cosmos Genesis Schema Browser</h1>
            <p class="subtitle">Open-source astrophysics data schemas for trillion-object scale</p>
        </header>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">89</div>
                <div class="stat-label">Total Schemas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">9</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">11</div>
                <div class="stat-label">Support Aging</div>
            </div>
        </div>

        <div class="categories">
"""

    # Generate category cards
    schemas = manifest.get('schemas', {})
    total_schemas = 0

    for category, schema_list in schemas.items():
        count = len(schema_list)
        total_schemas += count

        category_title = category.replace('_', ' ').title()

        html += f"""
            <div class="category-card">
                <h2 class="category-title">{category_title}</h2>
                <p class="category-count">{count} schema{"s" if count != 1 else ""}</p>
                <ul class="schema-list">
"""

        for schema in schema_list[:10]:  # Limit to first 10 for brevity
            schema_name = schema['name']
            html += f'                    <li><a href="#{schema_name.lower()}">{schema_name}</a></li>\n'

        if count > 10:
            html += f'                    <li style="color: #64748b; font-style: italic;">... and {count - 10} more</li>\n'

        html += """                </ul>
            </div>
"""

    html += """        </div>

        <footer>
            <p><strong>Cosmos Genesis™</strong> - We build the universe. You build the worlds.™</p>
            <p style="margin-top: 0.5rem;">
                <a href="https://cosmosgenesis.com">Website</a> •
                <a href="https://demo.cosmosgenesis.com">Demo</a> •
                <a href="https://github.com/cosmosgenesis/cosmos-schemas">GitHub</a>
            </p>
        </footer>
    </div>
</body>
</html>
"""

    output_file = output_dir / "index.html"
    output_file.write_text(html)
    print(f"✓ Generated {output_file}")
    print(f"  Total schemas: {total_schemas}")

def main():
    """Generate schema documentation"""
    print("Generating schema documentation...")

    # Load manifest
    manifest = load_manifest()

    # Create output directory
    output_dir = Path(__file__).parent.parent / "docs" / "schema-browser"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate index page
    generate_index_html(manifest, output_dir)

    print("\n✓ Documentation generated successfully!")
    print(f"  Output: {output_dir}")
    print("\nTo view locally:")
    print(f"  open {output_dir / 'index.html'}")

if __name__ == "__main__":
    main()
