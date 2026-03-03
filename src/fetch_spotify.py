"""
Fetch data from the Spotify Web API and store the raw response as JSON.

This script uses the Client Credentials flow to obtain an access token,
then queries the Spotify Search endpoint for artists.
"""

import base64
import json
import os
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv


SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_SEARCH_URL = 'https://api.spotify.com/v1/search'


def get_spotify_token(client_id: str, client_secret: str) -> str:
    """
    Get an access token using Spotify Client Credentials flow.
    """
    credentials = f'{client_id}:{client_secret}'
    encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {encoded}'
    }
    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(
        SPOTIFY_TOKEN_URL,
        headers=headers,
        data=data,
        timeout=30
    )
    response.raise_for_status()

    return response.json()['access_token']


def search_artists(query: str, token: str, limit: int = 10) -> dict:
    """
    Search for artists by query string.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'q': query,
        'type': 'artist',
        'limit': limit
    }

    response = requests.get(
        SPOTIFY_SEARCH_URL,
        headers=headers,
        params=params,
        timeout=30
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

    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    if client_id is None or client_secret is None:
        raise RuntimeError(
            'SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET is missing in .env.'
        )

    token = get_spotify_token(client_id, client_secret)

    query = 'taylor swift'
    result = search_artists(query=query, token=token, limit=10)

    payload = {
        'query': query,
        'result': result
    }

    filepath = save_json(payload, api_name='spotify')
    print(f'Successfully saved data to {filepath}')


if __name__ == '__main__':
    main()