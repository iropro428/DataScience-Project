"""
Create a small processed JSON from the latest Overpass raw export.

Extracts a compact list of OSM elements:
- id, type
- lat/lon (if present)
- a small subset of tags
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


RAW_DIR = Path('data/raw/overpass')
OUT_DIR = Path('data/processed/overpass')


def load_latest_raw_json(raw_dir: Path) -> dict[str, Any]:
    candidates = sorted(raw_dir.glob('*.json'))
    if not candidates:
        raise FileNotFoundError(f'No raw JSON files found in {raw_dir}.')

    latest = candidates[-1]
    return json.loads(latest.read_text(encoding='utf-8'))


def extract_elements(raw: dict[str, Any]) -> list[dict[str, Any]]:
    result = raw.get('result')
    if not isinstance(result, dict):
        return []

    data = result.get('data')
    if not isinstance(data, dict):
        return []

    elements = data.get('elements')
    if not isinstance(elements, list):
        return []

    cleaned: list[dict[str, Any]] = []

    for el in elements:
        if not isinstance(el, dict):
            continue

        tags = el.get('tags', {})
        if not isinstance(tags, dict):
            tags = {}

        # lat/lon für nodes
        lat = el.get('lat')
        lon = el.get('lon')

        # lat/lon für ways/relations
        center = el.get('center')
        if (lat is None or lon is None) and isinstance(center, dict):
            lat = center.get('lat')
            lon = center.get('lon')

        cleaned.append(
            {
                "osm_type": el.get("type"),
                "osm_id": el.get("id"),
                "lat": lat,
                "lon": lon,
                "name": tags.get("name"),
                "amenity": tags.get("amenity"),
                "leisure": tags.get("leisure"),
                "addr_city": tags.get("addr:city"),
                "addr_street": tags.get("addr:street"),
                "website": tags.get("website"),
                "operator": tags.get("operator"),
            }
        )

    return cleaned


def save_processed(payload: dict[str, Any]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.now().date().isoformat()
    out_file = OUT_DIR / f'{today}.json'

    out_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    return out_file


def main() -> None:
    raw = load_latest_raw_json(RAW_DIR)

    bbox = raw.get('bbox')
    elements = extract_elements(raw)

    payload = {
        'source': 'overpass',
        'bbox': bbox,
        'n_elements': len(elements),
        'elements': elements,
    }

    out_file = save_processed(payload)
    print(f'Successfully saved processed data to {out_file}')


if __name__ == '__main__':
    main()