# Last.fm artist.getTopTracks → Konzentrationsmetrik für F2
import requests, pandas as pd, time, os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "https://ws.audioscrobbler.com/2.0/"

try:
    from artists import ARTISTS
except ImportError:
    ARTISTS = pd.read_csv("data/raw/artists_list.csv")["name"].tolist()


def get_top_tracks(artist_name, limit=20):
    """
    Holt Top-Tracks eines Artists von Last.fm.
    Gibt eine Liste von (track_name, playcount) zurück.
    limit=20 reicht — wir brauchen nur Top-5 Anteil.
    """
    try:
        r = requests.get(BASE_URL, params={
            "method": "artist.getTopTracks",
            "artist": artist_name,
            "api_key": API_KEY,
            "format": "json",
            "limit": limit,
            "autocorrect": 1,
        }, timeout=10)
        data = r.json()
        tracks = data.get("toptracks", {}).get("track", [])
        if not tracks:
            return []
        return [
            {
                "artist_name": artist_name,
                "track_name": t.get("name"),
                "rank": int(t.get("@attr", {}).get("rank", i + 1)),
                "playcount": int(t.get("playcount", 0)),
            }
            for i, t in enumerate(tracks)
        ]
    except Exception as e:
        print(f"  ⚠️  {artist_name}: {e}")
        return []


# ── Main ──────────────────────────────────────────────────────────────────
all_tracks = []

for i, name in enumerate(ARTISTS):
    print(f"[{i + 1}/{len(ARTISTS)}] {name}", end=" ")
    tracks = get_top_tracks(name, limit=20)
    if tracks:
        all_tracks.extend(tracks)
        total_pc = sum(t["playcount"] for t in tracks)
        top5_pc = sum(t["playcount"] for t in tracks if t["rank"] <= 5)
        conc = top5_pc / total_pc * 100 if total_pc > 0 else 0
        print(f"→ {len(tracks)} Tracks | Top-5 Anteil: {conc:.1f}%")
    else:
        print("→ keine Daten")
    time.sleep(0.25)

# ── Speichern ─────────────────────────────────────────────────────────────
os.makedirs("data/raw", exist_ok=True)
df_tracks = pd.DataFrame(all_tracks)
df_tracks.to_csv("data/raw/lastfm_toptracks.csv", index=False)

print(f"\n✅ {len(df_tracks)} Track-Einträge → data/raw/lastfm_toptracks.csv")
print(f"   Artists mit Daten: {df_tracks['artist_name'].nunique()}")
