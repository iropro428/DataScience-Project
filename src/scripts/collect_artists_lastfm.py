'''
collect_artists_lastfm.py

Fetches basic artist metadata from the Last.fm API for a predefinded artist list and stores the results as a csv file.

What this script does:
1) Loads an API key from a .env file (LASTFM_API_KEY).
2) Iterates over ARTISTS (imported from artists.py).
3) For each artist, calls Last.fm "artist.getInfo".
4) Extracts a small, clean subset of fields (listeners, playcount, tags, url).
5) Writes everything to data/raw/last_fm/artists_lastfm.csv

'''
import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "https://ws.audioscrobbler.com/2.0/"

from artists import ARTISTS


def get_artist_data(artist_name):
    """
    Query Last.fm (artist.getinfo) and convert the response into one clean output row.

    Returns:
      dict with selected fields or None if the API signals an error / parsing fails.
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

        a = data["artist"]

        return {
            "name": a["name"],
            "lastfm_url": a["url"],
            "listeners": int(a["stats"]["listeners"]),  # = Spotify followers equivalent
            "playcount": int(a["stats"]["playcount"]),  # = Streams equivalent
            "tags": ", ".join([t["name"] for t in a["tags"]["tag"]]),  # = genres
            "collected_at": pd.Timestamp.now().isoformat()
        }

    except Exception as e:
        print(f"Fehler bei {artist_name}: {e}")
        return None


results = []

for i, name in enumerate(ARTISTS):
    print(f"[{i + 1}/{len(ARTISTS)}] Sammle: {name}")
    data = get_artist_data(name)
    if data:
        results.append(data)
        print(f"listeners={data['listeners']:,}  playcount={data['playcount']:,}")
    time.sleep(0.3) #gentle throttling to reduce rate-limit risk

df = pd.DataFrame(results)
os.makedirs("data", exist_ok=True)
df.to_csv("data/raw/artists_lastfm.csv", index=False)

print(f"\n Fertig! {len(df)} Artists → data/artists_lastfm.csv")
print(df[["name", "listeners", "playcount", "tags"]].to_string())
