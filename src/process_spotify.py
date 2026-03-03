"""
Create a small processed JSON from the latest Spotify raw export.

Extracts artist fields relevant for:
- follower count
- popularity score
- genres
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


RAW_DIR = Path('data/raw/spotify')
OUT_DIR = Path('data/processed/spotify')


def load_latest_raw_json(raw_dir: Path) -> dict[str, Any]:
    candidates = sorted(raw_dir.glob('*.json'))
    if not candidates:
        raise FileNotFoundError(f'No raw JSON files found in {raw_dir}.')

    latest = candidates[-1]
    return json.loads(latest.read_text(encoding='utf-8'))


def extract_artists(raw: dict[str, Any]) -> list[dict[str, Any]]:
    result = raw.get('result')
    if not isinstance(result, dict):
        return []

    artists_obj = result.get('artists')
    if not isinstance(artists_obj, dict):
        return []

    items = artists_obj.get('items')
    if not isinstance(items, list):
        return []

    out: list[dict[str, Any]] = []

    for it in items:
        if not isinstance(it, dict):
            continue

        followers = it.get('followers')
        follower_total = None
        if isinstance(followers, dict):
            follower_total = followers.get('total')

        out.append(
            {
                'artist_id': it.get('id'),
                'artist_name': it.get('name'),
                'popularity': it.get('popularity'),
                'followers_total': follower_total,
                'genres': it.get('genres', []),
                'spotify_url': (
                    it.get('external_urls', {}).get('spotify')
                    if isinstance(it.get('external_urls'), dict)
                    else None
                ),
            }
        )

    return out


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

    query = raw.get('query')
    artists = extract_artists(raw)

    payload = {
        'source': 'spotify',
        'query': query,
        'n_artists': len(artists),
        'artists': artists,
    }

    out_file = save_processed(payload)
    print(f'Successfully saved processed data to {out_file}')


if __name__ == '__main__':
    main()