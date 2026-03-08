# Holt Top-Artists von Last.fm Charts und speichert als:
#   src/scripts/artists.py ← Python-Liste, wird von anderen Scripts importiert
#   data/artists_list.csv ← CSV-Version als Backup
import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "https://ws.audioscrobbler.com/2.0/"


def get_top_artists(pages=10):
    """
    1 page = 50 artists
    pages=10 → 500 artists (empfohlen)
    pages=5  → 250 artists (schneller)
    """
    all_artists = []

    for page in range(1, pages + 1):
        print(f"  Seite {page}/{pages}...")
        try:
            r = requests.get(BASE_URL, params={
                "method": "chart.gettopartists",
                "api_key": API_KEY,
                "format": "json",
                "limit": 50,
                "page": page,
            }, timeout=10)
            data = r.json()
            artists = data.get("artists", {}).get("artist", [])
            for a in artists:
                name = a.get("name", "").strip()
                if name:
                    all_artists.append(name)
        except Exception as e:
            print(f"  ⚠️  Fehler Seite {page}: {e}")
        time.sleep(0.3)

    return all_artists


# ── Ausführen ──────────────────────────────────────────────────────────────
print("🎵 Lade Top-Artists von Last.fm Charts...")
artists = get_top_artists(pages=10)  # = 500 Artists

# Duplikate entfernen, Reihenfolge beibehalten
seen = set()
artists_unique = []
for a in artists:
    if a not in seen:
        seen.add(a)
        artists_unique.append(a)

print(f"✅ {len(artists_unique)} einzigartige Artists gesammelt")

# ── Als src/scripts/artists.py speichern ───────────────────────────────────────────────
with open("src/scripts/artists.py", "w", encoding="utf-8") as f:
    f.write("# Automatisch generiert von get_artists_list.py\n")
    f.write("# Last.fm Top-Artists (chart.gettopartists)\n\n")
    f.write("ARTISTS = [\n")
    for name in artists_unique:
        escaped = name.replace("\\", "\\\\").replace('"', '\\"')
        f.write(f'    "{escaped}",\n')
    f.write("]\n")

print("✅ src/scripts/artists.py gespeichert")

# ── Als CSV speichern ──────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
pd.DataFrame({"name": artists_unique}).to_csv("data/raw/artists_list.csv", index=False)
print("✅ data/artists_list.csv gespeichert")

print(f"\nErste 10 Artists:")
for a in artists_unique[:10]:
    print(f"  {a}")
