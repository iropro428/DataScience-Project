import requests
import pandas as pd
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
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
    print("LASTFM_API_KEY is not set. Please add it to your .env file.")
    import sys
    sys.exit(1)

BASE_URL = "https://ws.audioscrobbler.com/2.0/"
OUTPUT = Path("data/raw/lastfm_geo_presence.csv")
LIMIT = 200  # Top-N artists per country
DELAY = 0.25  # Seconds between requests to reduce rate-limit risks
COUNTRY_NAME_MAP = {
    "Great Britain": "United Kingdom",
    "United States Of America": "United States",
}


def load_tour_countries() -> list:
    """
    Build the list of countries we want to query on Last.fm.

    We first try a processed file (cleaner), and if that does not exist,
    we fall back to the raw Ticketmaster events.

    Returns:
        Sorted list of unique country names.
    """
    sources = [
        "data/processed/f4_city_frequencies.csv",
        "data/raw/ticketmaster_events.csv",
    ]

    for src in sources:
        if os.path.exists(src):
            df = pd.read_csv(src)
            if "country" in df.columns:
                countries = (
                    df["country"]
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .unique()
                    .tolist()
                )
                print(f"Loaded {len(countries)} countries from {src}")
                return sorted(countries)

    print("Could not find any input file with a 'country' column.")
    import sys
    sys.exit(1)


def get_top_artists_for_country(country: str) -> list:
    """
    Query Last.fm geo.getTopArtists for the top artists in a given country.

    Returns:
        List of tuples: (artist_name, rank, listeners_in_country)
    """
    lastfm_country = COUNTRY_NAME_MAP.get(country, country)

    try:
        r = requests.get(
            BASE_URL,
            params={
                "method": "geo.getTopArtists",
                "country": lastfm_country,
                "limit": LIMIT,
                "api_key": LASTFM_KEY,
                "format": "json",
            },
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()

        if "error" in data:
            print(f"{country} -> {lastfm_country}: Last.fm error {data['error']} — {data.get('message', '')}")
            return []

        artists = data.get("topartists", {}).get("artist", [])
        result = []

        for i, a in enumerate(artists, start=1):
            name = a.get("name", "").strip()
            if not name:
                continue

            listeners = int(a.get("listeners", 0) or 0)
            rank = int(a.get("@attr", {}).get("rank", i))

            result.append((name, rank, listeners))

        return result

    except Exception as e:
        print(f"{country} -> {lastfm_country}: {e}")
        return []


def main():
    countries = load_tour_countries()
    print(f"Starting Last.fm geo.getTopArtists for {len(countries)} countries...")
    print(f"Limit: Top {LIMIT} artists per country\n")

    all_rows = []

    for i, country in enumerate(countries, start=1):
        artists = get_top_artists_for_country(country)
        n = len(artists)
        print(f"[{i:>3}/{len(countries)}] {country:<30} -> {n} artists")

        for artist_name, rank, listeners in artists:
            all_rows.append(
                {
                    "country": country,
                    "artist_name": artist_name,
                    "rank": rank,
                    "listeners_in_country": listeners,
                }
            )

        time.sleep(DELAY)

    if not all_rows:
        print("No data collected.")
        return

    df = pd.DataFrame(all_rows)

    # Normalize names for later joins (case-insensitive matching)
    df["artist_norm"] = df["artist_name"].astype(str).str.lower().str.strip()

    # Ensure numeric types
    df["listeners_in_country"] = (
        pd.to_numeric(df["listeners_in_country"], errors="coerce")
        .fillna(0)
        .astype(int)
    )
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce").fillna(LIMIT + 1).astype(int)

    # Sort so each artist's strongest countries come first
    df = df.sort_values(
        by=["artist_name", "listeners_in_country", "rank"],
        ascending=[True, False, True],
    ).reset_index(drop=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    print(f"\nSaved {len(df)} rows to -> {OUTPUT}")
    print(f"{df['country'].nunique()} countries")
    print(f"{df['artist_name'].nunique()} unique artists")

    print("\nTop artists globally (by number of country charts they appear in):")
    top = (
        df.groupby("artist_name")["country"]
        .count()
        .sort_values(ascending=False)
        .head(10)
    )
    print(top.to_string())


if __name__ == "__main__":
    main()
