"""
Fetch data from the Overpass API (OpenStreetMap) and store the raw response
as a JSON file in the data directory.

The example query fetches up to 50 cafes within
a small bounding box around Kiel.
"""

import json
from datetime import date
from pathlib import Path

import requests


OVERPASS_URLS = [
    'https://overpass.kumi.systems/api/interpreter',
    'https://overpass-api.de/api/interpreter',
    'https://overpass.openstreetmap.ru/api/interpreter',
    'https://overpass.nchc.org.tw/api/interpreter'
]


def build_concert_venue_query(bbox: tuple[float, float, float, float]) -> str:
    """
    Build an Overpass QL query for concert venues in a bounding box.

    We fetch nodes/ways/relations for common venue tags and use 'out center'
    so ways/relations also get a coordinate.
    """
    south, west, north, east = bbox

    return (
        '[out:json][timeout:25];'
        '('
        f'node["amenity"="concert_hall"]({south},{west},{north},{east});'
        f'way["amenity"="concert_hall"]({south},{west},{north},{east});'
        f'relation["amenity"="concert_hall"]({south},{west},{north},{east});'

        f'node["amenity"="theatre"]({south},{west},{north},{east});'
        f'way["amenity"="theatre"]({south},{west},{north},{east});'
        f'relation["amenity"="theatre"]({south},{west},{north},{east});'

        f'node["amenity"="arts_centre"]({south},{west},{north},{east});'
        f'way["amenity"="arts_centre"]({south},{west},{north},{east});'
        f'relation["amenity"="arts_centre"]({south},{west},{north},{east});'

        f'node["amenity"="nightclub"]({south},{west},{north},{east});'
        f'way["amenity"="nightclub"]({south},{west},{north},{east});'
        f'relation["amenity"="nightclub"]({south},{west},{north},{east});'

        f'node["leisure"="stadium"]({south},{west},{north},{east});'
        f'way["leisure"="stadium"]({south},{west},{north},{east});'
        f'relation["leisure"="stadium"]({south},{west},{north},{east});'

        f'node["leisure"="sports_hall"]({south},{west},{north},{east});'
        f'way["leisure"="sports_hall"]({south},{west},{north},{east});'
        f'relation["leisure"="sports_hall"]({south},{west},{north},{east});'
        ');'
        'out tags center;'
    )


def fetch_overpass(query: str) -> dict:
    """
    Send an Overpass QL query to the first working Overpass instance.

    Parameters
    ----------
    query : str
        Overpass QL query.

    Returns
    -------
    dict
        A dict containing the server URL and the JSON response data.
    """
    last_error: Exception | None = None

    for url in OVERPASS_URLS:
        try:
            response = requests.post(
                url,
                data={'data': query},
                timeout=120
            )
            response.raise_for_status()

            return {
                'server': url,
                'data': response.json()
            }
        except (requests.RequestException, ValueError) as error:
            last_error = error

    raise RuntimeError('All Overpass servers failed.') from last_error


def save_json(payload: dict, api_name: str) -> Path:
    """
    Save JSON payload to data/raw/<api_name>/YYYY-MM-DD.json.
    """
    output_dir = Path('data/raw') / api_name
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f'{date.today().isoformat()}.json'
    filepath = output_dir / filename

    filepath.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    return filepath


def main() -> None:
    """
    Main execution function.
    """
    bbox = (54.28, 10.05, 54.38, 10.20)

    query = build_concert_venue_query(bbox)
    result = fetch_overpass(query)

    payload = {
        'bbox': bbox,
        'query': query,
        'result': result
    }

    filepath = save_json(payload, api_name='overpass')
    print(f'Successfully saved data to {filepath}')


if __name__ == '__main__':
    main()