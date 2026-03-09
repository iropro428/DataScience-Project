# Processes Spotify Weekly Chart CSVs → artist profile table
#
# Input:  data/raw/spotify_charts/*.csv
#         (filename must contain YYYY-MM-DD, e.g., regional-global-weekly-2023-02-23.csv)
#
# Output:
#   data/processed/spotify_charts/chart_artists.csv ← Haupt-Output for F3
#   data/processed/spotify_charts/spotify_artist_streams_monthly.json

import pandas as pd
import glob
import re
import json
import os
from pathlib import Path

INPUT_GLOB = "data/raw/spotify_charts/*.csv"
OUTPUT_DIR = Path("data/processed/spotify_charts")
OUTPUT_ARTISTS = OUTPUT_DIR / "chart_artists.csv"
OUTPUT_MONTHLY = OUTPUT_DIR / "spotify_artist_streams_monthly.json"

DATE_START = "2023-02-01"
DATE_END = "2026-02-28"


def extract_date(filename: str) -> str:
    m = re.search(r"\d{4}-\d{2}-\d{2}", filename)
    if not m:
        raise ValueError(f"Kein Datum im Dateinamen: {filename}")
    return m.group(0)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {}
    for c in df.columns:
        name = c.strip().lower()
        if name in ["artist", "artist_names", "artists"]:
            col_map[c] = "artist"
        elif name in ["track", "track_name", "track name"]:
            col_map[c] = "track"
        elif name in ["streams", "stream"]:
            col_map[c] = "streams"
        elif name in ["position", "rank"]:
            col_map[c] = "position"
        elif name in ["weeks_on_chart", "weeks on chart"]:
            col_map[c] = "weeks_on_chart"
        elif name in ["uri", "url"]:
            col_map[c] = "uri"

    df = df.rename(columns=col_map)

    if "artist" not in df.columns or "streams" not in df.columns:
        raise KeyError(f"Missing required columns. Found: {list(df.columns)}")

    # Clean streams
    df["streams"] = (
        pd.to_numeric(
            df["streams"].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        ).fillna(0).astype(int)
    )

    # Position (optional)
    if "position" in df.columns:
        df["position"] = pd.to_numeric(df["position"], errors="coerce").fillna(9999).astype(int)

    # weeks_on_chart (optional)
    if "weeks_on_chart" in df.columns:
        df["weeks_on_chart"] = pd.to_numeric(df["weeks_on_chart"], errors="coerce").fillna(0).astype(int)

    # Split collaborations: "Artist A, Artist B" → two rows
    df["artist"] = df["artist"].astype(str).str.strip()
    df["artist"] = df["artist"].str.split(", ")
    df = df.explode("artist")
    df["artist"] = df["artist"].str.strip()
    df = df[df["artist"] != ""]

    return df


def main():
    files = sorted(glob.glob(INPUT_GLOB))
    if not files:
        print(f"   No CSV files found: {INPUT_GLOB}")
        print("    Copy Spotify chart CSVs to data/raw/spotify_charts/")
        return

    print(f"  {len(files)} Chart files found")

    all_frames = []
    skipped = 0

    for f in files:
        date_str = extract_date(f)
        # Date filter Feb 2023 – Feb 2026
        if not (DATE_START <= date_str <= DATE_END):
            skipped += 1
            continue
        try:
            df = pd.read_csv(f, encoding="utf-8-sig")
            df = normalize_columns(df)
            df["week_date"] = pd.to_datetime(date_str)
            all_frames.append(df)
        except Exception as e:
            print(f"     {os.path.basename(f)}: {e}")

    if not all_frames:
        print("No usable data after applying the date filter")
        return

    print(f"  {len(all_frames)} Weeks loaded  |  {skipped} outside the time period")

    data = pd.concat(all_frames, ignore_index=True)

    # Monthly aggregation
    data["month"] = data["week_date"].dt.to_period("M").astype(str)

    monthly = (
        data.groupby(["month", "week_date", "artist"], as_index=False)["streams"]
        .sum()
        .rename(columns={"week_date": "sample_week_date", "streams": "streams_sample_week"})
        .sort_values(["month", "streams_sample_week"], ascending=[True, False])
    )
    monthly["sample_week_date"] = monthly["sample_week_date"].dt.strftime("%Y-%m-%d")

    # Artist profile table (for F3 join)
    # Per artist: total streams, number of weeks in the chart, peak position, peak month
    agg = {"streams": "sum", "week_date": "count"}
    if "position" in data.columns:
        agg["position"] = "min"  # best (= lowest) position

    artist_profile = (
        data.groupby("artist")
        .agg(**{
            "total_chart_streams": ("streams", "sum"),
            "chart_weeks": ("week_date", "nunique"),
            "peak_position": ("position", "min") if "position" in data.columns
            else ("streams", "count"),
        })
        .reset_index()
        .sort_values("total_chart_streams", ascending=False)
    )
    # Time period of the first / last chart appearance
    first_last = data.groupby("artist")["week_date"].agg(
        first_chart_date="min", last_chart_date="max"
    ).reset_index()
    first_last["first_chart_date"] = first_last["first_chart_date"].dt.strftime("%Y-%m-%d")
    first_last["last_chart_date"] = first_last["last_chart_date"].dt.strftime("%Y-%m-%d")
    artist_profile = artist_profile.merge(first_last, on="artist", how="left")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    artist_profile.to_csv(OUTPUT_ARTISTS, index=False)
    with open(OUTPUT_MONTHLY, "w") as f_out:
        json.dump(monthly.to_dict(orient="records"), f_out, indent=2)

    print(f"\n  {len(artist_profile)} Chart-Artists → {OUTPUT_ARTISTS}")
    print(f"  Monthly data            → {OUTPUT_MONTHLY}")

    print(f"\n--- Quick check ---")
    print(f"  Time period:    {data['week_date'].min().date()} – {data['week_date'].max().date()}")
    print(f"  Chart-Weeks:    {data['week_date'].nunique()}")
    print(f"  Chart-Artists:  {len(artist_profile)}")
    print(f"\nTop 10 Artists by total streams:")
    print(artist_profile.head(10)[["artist", "total_chart_streams", "chart_weeks", "peak_position"]].to_string(index=False))


if __name__ == "__main__":
    main()
