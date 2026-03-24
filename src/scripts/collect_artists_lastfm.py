# =============================================================================
# AI was used exclusively for debugging purposes,
# not for the creation or generation of the code itself.
# =============================================================================


# collect_artists_lastfm.py
#
# Fetches basic artist metadata from the Last.fm API for a predefined artist list and stores the results as a CSV file.
#
# What this script does:
# 1) Loads an API key from a .env file (LASTFM_API_KEY).
# 2) Iterates over ARTISTS (imported from artists.py).
# 3) For each artist, calls Last.fm "artist.getInfo".
# 4) Extracts a small, clean subset of fields (listeners, playcount, tags, url).
# 5) Writes everything to data/raw/last_fm/artists_lastfm.csv

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from artists import ARTISTS

# Load environment variables
load_dotenv()

# Constants
API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "https://ws.audioscrobbler.com/2.0/"

def get_artist_data(artist_name):
    """
    Query Last.fm (artist.getinfo) and convert the response into one clean output row.

    Args:
      artist_name (str): The name of the artist to query.

    Returns:
      dict: A dictionary with selected fields or None if the API signals an error / parsing fails.
    """
    try:
        params = {
            "method": "artist.getinfo",
            "artist": artist_name,
            "api_key": API_KEY,
            "format": "json"
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if "error" in data:
            print(f"{artist_name}: {data['message']}")
            return None

        artist_data = data["artist"]

        return {
            "name": artist_data["name"],
            "lastfm_url": artist_data["url"],
            "listeners": int(artist_data["stats"]["listeners"]),  # = Spotify followers equivalent
            "playcount": int(artist_data["stats"]["playcount"]),  # = Streams equivalent
            "tags": ", ".join([tag["name"] for tag in artist_data["tags"]["tag"]]),  # = genres
            "collected_at": pd.Timestamp.now().isoformat()
        }

    except Exception as e:
        print(f"Error while processing {artist_name}: {e}")
        return None


# Main process
results = []

for i, artist_name in enumerate(ARTISTS):
    print(f"[{i + 1}/{len(ARTISTS)}] Collecting data for: {artist_name}")
    data = get_artist_data(artist_name)
    if data:
        results.append(data)
        print(f"listeners={data['listeners']:,}  playcount={data['playcount']:,}")
    time.sleep(0.3)  # Gentle throttling to reduce rate-limit risk

# Save results to CSV
df = pd.DataFrame(results)
os.makedirs("data", exist_ok=True)
df.to_csv("data/raw/artists_lastfm.csv", index=False)

print(f"\nDone! {len(df)} artists → data/artists_lastfm.csv")
print(df[["name", "listeners", "playcount", "tags"]].to_string())
