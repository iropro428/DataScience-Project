import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "https://ws.audioscrobbler.com/2.0/"

# Load artists list
try:
    from artists import ARTISTS
except ImportError:
    ARTISTS = pd.read_csv("data/raw/artists_list.csv")["name"].tolist()


def get_top_tracks(artist_name, limit=20):
    """
    Fetches the top tracks of an artist from Last.fm.
    Returns a list of (track_name, playcount).
    
    Args:
        artist_name (str): Name of the artist.
        limit (int): Number of top tracks to fetch (default is 20).
        
    Returns:
        list: A list of dictionaries containing 'track_name', 'rank', and 'playcount'.
    """
    try:
        response = requests.get(
            BASE_URL,
            params={
                "method": "artist.getTopTracks",
                "artist": artist_name,
                "api_key": API_KEY,
                "format": "json",
                "limit": limit,
                "autocorrect": 1,
            },
            timeout=10
        )
        data = response.json()
        tracks = data.get("toptracks", {}).get("track", [])

        if not tracks:
            return []

        return [
            {
                "artist_name": artist_name,
                "track_name": track.get("name"),
                "rank": int(track.get("@attr", {}).get("rank", i + 1)),
                "playcount": int(track.get("playcount", 0)),
            }
            for i, track in enumerate(tracks)
        ]
    except Exception as e:
        print(f"{artist_name}: {e}")
        return []


# Main process
all_tracks = []

for i, name in enumerate(ARTISTS):
    print(f"[{i + 1}/{len(ARTISTS)}] {name}", end=" ")
    tracks = get_top_tracks(name, limit=20)

    if tracks:
        all_tracks.extend(tracks)
        total_playcount = sum(track["playcount"] for track in tracks)
        top5_playcount = sum(track["playcount"] for track in tracks if track["rank"] <= 5)
        top5_percentage = top5_playcount / total_playcount * 100 if total_playcount > 0 else 0
        print(f"→ {len(tracks)} Tracks | Top-5 Share: {top5_percentage:.1f}%")
    else:
        print("→ No data available")
    
    time.sleep(0.25)

# Save the results
os.makedirs("data/raw", exist_ok=True)
df_tracks = pd.DataFrame(all_tracks)
df_tracks.to_csv("data/raw/lastfm_toptracks.csv", index=False)

print(f"\n{len(df_tracks)} track entries saved → data/raw/lastfm_toptracks.csv")
print(f"   Artists with data: {df_tracks['artist_name'].nunique()}")