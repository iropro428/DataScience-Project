# collect_artists_lastfm.py
import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "https://ws.audioscrobbler.com/2.0/"

from alt.artists import ARTISTS


def get_artist_data(artist_name):
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
    time.sleep(0.3)

df = pd.DataFrame(results)
os.makedirs("data", exist_ok=True)
df.to_csv("data/raw/last_fm/artists_lastfm.csv", index=False)

print(f"\n Fertig! {len(df)} Artists → data/artists_lastfm.csv")
print(df[["name", "listeners", "playcount", "tags"]].to_string())
