"""
Fetch directions from the OpenRouteService API and store the raw response
as a JSON file in the data directory.

This example requests a driving-car route between two coordinates.
"""

import json
import os
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv


ORS_DIRECTIONS_URL = 'https://api.openrouteservice.org/v2/directions/driving-car'


def fetch_directions(
    api_key: str,
    start: tuple[float, float],
    end: tuple[float, float]
) -> dict:
    """
    Fetch a route from OpenRouteService.

    Parameters
    ----------
    api_key : str
        OpenRouteService API key.
    start : tuple[float, float]
        Start coordinate as (lon, lat).
    end : tuple[float, float]
        End coordinate as (lon, lat).

    Returns
    -------
    dict
        JSON response from ORS directions endpoint.
    """
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    body = {
        'coordinates': [
            [start[0], start[1]],
            [end[0], end[1]]
        ]
    }

    response = requests.post(
        ORS_DIRECTIONS_URL,
        headers=headers,
        json=body,
        timeout=60
    )
    response.raise_for_status()

    return response.json()


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
    load_dotenv()

    api_key = os.getenv('OPENROUTESERVICE_KEY')
    if api_key is None:
        raise RuntimeError('OPENROUTESERVICE_KEY is missing in the .env file.')

    # Example coordinates (Kiel): start = Kiel Hbf, end = CAU Kiel
    start = (10.1328, 54.3233)  # (lon, lat)
    end = (10.1086, 54.3383)    # (lon, lat)

    route = fetch_directions(api_key=api_key, start=start, end=end)

    payload = {
        'start': start,
        'end': end,
        'profile': 'driving-car',
        'route': route
    }

    filepath = save_json(payload, api_name='openrouteservice')
    print(f'Successfully saved data to {filepath}')


if __name__ == '__main__':
    main()