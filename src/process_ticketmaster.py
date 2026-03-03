"""
Create a small processed JSON from the latest Ticketmaster raw export.

Extracts event fields relevant for:
- ticket availability (on sale / off sale)
- time & scheduling (event date, weekday/weekend)
- price ranges (min/max)
- geographic fields (city/country + optional coordinates if available)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


RAW_DIR = Path('data/raw/ticketmaster')
OUT_DIR = Path('data/processed/ticketmaster')


def load_latest_raw_json(raw_dir: Path) -> dict[str, Any]:
    """
    Load the newest JSON file from a raw directory.
    """
    candidates = sorted(raw_dir.glob('*.json'))
    if not candidates:
        raise FileNotFoundError(f'No raw JSON files found in {raw_dir}.')

    latest = candidates[-1]
    return json.loads(latest.read_text(encoding='utf-8'))


def safe_get(dct: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    """
    Safe nested dict getter.
    """
    cur: Any = dct
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def is_weekend(date_time_iso: str | None) -> bool | None:
    """
    Return True if date is Saturday/Sunday, else False. None if unknown.
    """
    if not date_time_iso:
        return None

    try:
        dt = datetime.fromisoformat(date_time_iso.replace('Z', '+00:00'))
    except ValueError:
        return None

    return dt.weekday() >= 5


def extract_events(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extract a compact list of event summaries.
    """
    events = safe_get(raw, ['_embedded', 'events'], default=[])
    if not isinstance(events, list):
        return []

    out: list[dict[str, Any]] = []

    for ev in events:
        if not isinstance(ev, dict):
            continue

        event_id = ev.get('id')
        name = ev.get('name')
        url = ev.get('url')

        status_code = safe_get(ev, ['dates', 'status', 'code'])
        event_dt = safe_get(ev, ['dates', 'start', 'dateTime'])
        local_date = safe_get(ev, ['dates', 'start', 'localDate'])
        local_time = safe_get(ev, ['dates', 'start', 'localTime'])
        weekend = is_weekend(event_dt)

        venue = None
        city = None
        country = None
        lat = None
        lon = None

        venues = safe_get(ev, ['_embedded', 'venues'], default=[])
        if isinstance(venues, list) and venues:
            v0 = venues[0]
            if isinstance(v0, dict):
                venue = v0.get('name')
                city = safe_get(v0, ['city', 'name'])
                country = safe_get(v0, ['country', 'countryCode'])

                loc = v0.get('location')
                if isinstance(loc, dict):
                    lat = loc.get('latitude')
                    lon = loc.get('longitude')

        price_min = None
        price_max = None
        currency = None

        price_ranges = ev.get('priceRanges')
        if isinstance(price_ranges, list) and price_ranges:
            pr0 = price_ranges[0]
            if isinstance(pr0, dict):
                price_min = pr0.get('min')
                price_max = pr0.get('max')
                currency = pr0.get('currency')

        out.append(
            {
                'event_id': event_id,
                'event_name': name,
                'url': url,
                'status': status_code,
                'dateTime_utc': event_dt,
                'local_date': local_date,
                'local_time': local_time,
                'is_weekend': weekend,
                'venue': venue,
                'city': city,
                'country': country,
                'latitude': lat,
                'longitude': lon,
                'price_min': price_min,
                'price_max': price_max,
                'currency': currency,
            }
        )

    return out


def save_processed(payload: dict[str, Any]) -> Path:
    """
    Save processed JSON to data/processed/ticketmaster/YYYY-MM-DD.json.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.now().date().isoformat()
    out_file = OUT_DIR / f'{today}.json'

    out_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    return out_file


def main() -> None:
    """
    Main execution.
    """
    raw = load_latest_raw_json(RAW_DIR)
    events = extract_events(raw)

    payload = {
        'source': 'ticketmaster',
        'n_events': len(events),
        'events': events,
    }

    out_file = save_processed(payload)
    print(f'Successfully saved processed data to {out_file}')


if __name__ == '__main__':
    main()