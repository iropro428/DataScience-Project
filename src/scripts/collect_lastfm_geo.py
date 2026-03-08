# collect_lastfm_geo.py
# Sammelt fuer jedes Land in den Ticketmaster-Daten die Top-Kuenstler von Last.fm.
# Dadurch wissen wir: In welchen Laendern ist ein Artist auf Last.fm prominent?
#
# Last.fm Endpunkt: geo.getTopArtists(country=X, limit=50)
# → Ruft pro Land die Top-50-Artists ab → invertiert zu: Artist → [Laender]
#
# Input:  data/processed/f4_city_frequencies.csv  (enthaelt country-Spalte)
#         oder data/raw/ticketmaster_events.csv
# Output: data/raw/lastfm_geo_presence.csv
#         Spalten: artist_name, country, rank (Position im Laender-Chart)

import requests
import pandas as pd
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# .env laden
_script_dir = Path(__file__).resolve().parent
for _candidate in [
    _script_dir / ".env",
    _script_dir.parent / ".env",
    _script_dir.parent.parent / ".env",
]:
    if _candidate.exists():
        load_dotenv(_candidate)
        break
else:
    load_dotenv()

LASTFM_KEY = os.getenv("LASTFM_API_KEY")
if not LASTFM_KEY:
    print("❌ LASTFM_API_KEY nicht gesetzt")
    import sys;

    sys.exit(1)

BASE_URL = "http://ws.audioscrobbler.com/2.0/"
OUTPUT = Path("data/raw/lastfm_geo_presence.csv")
LIMIT = 50  # Top-N Artists pro Land
DELAY = 0.25  # Sekunden zwischen Requests


# ── Laender aus Ticketmaster-Daten laden ─────────────────────────────────
def load_tour_countries() -> list:
    sources = [
        "data/processed/f4_city_frequencies.csv",
        "data/raw/ticketmaster_events.csv",
    ]
    for src in sources:
        if os.path.exists(src):
            df = pd.read_csv(src)
            if "country" in df.columns:
                countries = df["country"].dropna().unique().tolist()
                print(f"✅ {len(countries)} Laender aus {src}")
                return sorted(countries)
    print("❌ Keine Laender-Quelle gefunden")
    import sys;
    sys.exit(1)


def get_top_artists_for_country(country: str) -> list:
    """
    Ruft Last.fm geo.getTopArtists fuer ein Land ab.
    Gibt Liste von (artist_name, rank) zurueck.
    """
    try:
        r = requests.get(BASE_URL, params={
            "method": "geo.getTopArtists",
            "country": country,
            "limit": LIMIT,
            "api_key": LASTFM_KEY,
            "format": "json",
        }, timeout=10)
        r.raise_for_status()
        data = r.json()

        # Fehler-Check: Last.fm gibt manchmal {"error": 6} fuer unbekannte Laender
        if "error" in data:
            print(f"  ⚠️  {country}: Last.fm Fehler {data['error']} — {data.get('message', '')}")
            return []

        artists = data.get("topartists", {}).get("artist", [])
        result = []
        for i, a in enumerate(artists):
            name = a.get("name", "").strip()
            if not name:
                continue
            listeners = int(a.get("listeners", 0) or 0)
            result.append((name, i + 1, listeners))  # (name, rank, listeners)
        return result

    except Exception as e:
        print(f"  ❌ {country}: {e}")
        return []


def main():
    countries = load_tour_countries()
    print(f"📡 Starte Last.fm geo.getTopArtists fuer {len(countries)} Laender...")
    print(f"   Limit: Top {LIMIT} Artists pro Land\n")

    all_rows = []

    for i, country in enumerate(countries, 1):
        artists = get_top_artists_for_country(country)
        n = len(artists)
        print(f"  [{i:>3}/{len(countries)}] {country:<30} → {n} Artists")

        for artist_name, rank, listeners in artists:
            all_rows.append({
                "country": country,
                "artist_name": artist_name,
                "rank": rank,
                "listeners_in_country": listeners,
            })

        time.sleep(DELAY)

    if not all_rows:
        print("❌ Keine Daten gesammelt")
        return

    df = pd.DataFrame(all_rows)

    # Normalisiere Namen fuer spaetere Joins
    df["artist_norm"] = df["artist_name"].str.lower().str.strip()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    print(f"\n✅ {len(df)} Eintraege gespeichert → {OUTPUT}")
    print(f"   {df['country'].nunique()} Laender")
    print(f"   {df['artist_name'].nunique()} einzigartige Artists")
    print(f"\nTop Artists global (meiste Laender-Charts):")
    top = (df.groupby("artist_name")["country"]
           .count()
           .sort_values(ascending=False)
           .head(10))
    print(top.to_string())


if __name__ == "__main__":
    main()
