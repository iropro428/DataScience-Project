"""
Fetch events from the Ticketmaster API and store the raw
response as a JSON file in the data directory.
"""

import json
import os
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv


def fetch_ticketmaster_events(
    keyword: str,
    country_code: str,
    size: int = 50
) -> dict:
    """
    Fetch events from Ticketmaster API.

    Parameters
    ----------
    keyword : str
        Search keyword (e.g. 'concert').
    country_code : str
        ISO country code (e.g. 'DE').
    size : int
        Number of events to retrieve.

    Returns
    -------
    dict
        JSON response from Ticketmaster API.
    """
    load_dotenv()

    api_key = os.getenv('TICKETMASTER_KEY')
    if api_key is None:
        raise RuntimeError(
            'TICKETMASTER_KEY is missing in the .env file.'
        )

    url = 'https://app.ticketmaster.com/discovery/v2/events.json'

    params = {
        'apikey': api_key,
        'keyword': keyword,
        'size': size,
        'countryCode': country_code,
        'sort': 'date,asc'
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def save_json(data: dict, api_name: str) -> Path:
    """
    Save JSON data to data/raw/<api_name>/YYYY-MM-DD.json.
    """
    output_dir = Path('data/raw') / api_name
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f'{date.today().isoformat()}.json'
    filepath = output_dir / filename

    filepath.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    return filepath


def main() -> None:
    """
    Main execution function.
    """
    data = fetch_ticketmaster_events(
        keyword='concert',
        country_code='DE',
        size=50
    )

    filepath = save_json(data, api_name='ticketmaster')

    print(f'Successfully saved data to {filepath}')


if __name__ == '__main__':
    main()