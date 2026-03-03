"""
Create a small processed JSON from the latest OpenRouteService raw export.

Extracts route summary fields relevant for:
- distance (meters)
- duration (seconds)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


RAW_DIR = Path('data/raw/openrouteservice')
OUT_DIR = Path('data/processed/openrouteservice')


def load_latest_raw_json(raw_dir: Path) -> dict[str, Any]:
    candidates = sorted(raw_dir.glob('*.json'))
    if not candidates:
        raise FileNotFoundError(f'No raw JSON files found in {raw_dir}.')

    latest = candidates[-1]
    return json.loads(latest.read_text(encoding='utf-8'))


def safe_get(dct: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    cur: Any = dct
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def extract_route_summary(raw: dict[str, Any]) -> dict[str, Any]:
    route = raw.get('route')
    if not isinstance(route, dict):
        return {}

    routes = route.get('routes')
    if not isinstance(routes, list) or not routes:
        return {}

    first_route = routes[0]
    if not isinstance(first_route, dict):
        return {}

    summary = first_route.get('summary')
    if not isinstance(summary, dict):
        return {}

    distance = summary.get('distance')
    duration = summary.get('duration')

    return {
        'profile': raw.get('profile'),
        'start': raw.get('start'),
        'end': raw.get('end'),
        'distance_m': distance,
        'duration_s': duration,
    }


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
    summary = extract_route_summary(raw)

    payload = {
        'source': 'openrouteservice',
        'route_summary': summary,
    }

    out_file = save_processed(payload)
    print(f'Successfully saved processed data to {out_file}')


if __name__ == '__main__':
    main()