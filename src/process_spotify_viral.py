"""
Create a processed dataset of "viral hits" from Spotify weekly chart CSVs.

Input:  data/spotify_charts/regional-global-weekly-YYYY-MM-DD.csv
Output: data/processed/spotify_viral_hits.json

Definition (configurable):
- viral_hit: position <= 10 AND weeks_on_chart <= 4
This approximates "high popularity + recent release" using chart data.
"""

import glob
import json
import re
from pathlib import Path

import pandas as pd

INPUT_GLOB = "data/raw/spotify_charts/*.csv"
OUTPUT_PATH = Path("data/processed/spotify_charts/spotify_viral_hits.json")


def extract_date_from_filename(path: str) -> str:
    m = re.search(r"\d{4}-\d{2}-\d{2}", path)
    if not m:
        raise ValueError(f"Could not find YYYY-MM-DD in filename: {path}")
    return m.group(0)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Map various export formats to standard names
    col_map = {}
    for c in df.columns:
        cc = c.strip().lower()
        if cc in ["artist", "artist_names", "artists"]:
            col_map[c] = "artist"
        elif cc in ["track", "track_name", "track name"]:
            col_map[c] = "track"
        elif cc in ["streams", "stream"]:
            col_map[c] = "streams"
        elif cc in ["position", "rank"]:
            col_map[c] = "position"
        elif cc in ["weeks_on_chart", "weeks on chart"]:
            col_map[c] = "weeks_on_chart"
        elif cc in ["uri", "url"]:
            col_map[c] = "uri"

    df = df.rename(columns=col_map)

    required = {"artist", "track", "streams", "position", "weeks_on_chart"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns {missing}. Found: {list(df.columns)}")

    # numeric cleanup
    df["streams"] = (
        df["streams"].astype(str).str.replace(",", "", regex=False).str.strip()
    )
    df["streams"] = pd.to_numeric(df["streams"], errors="coerce").fillna(0).astype(int)

    df["position"] = pd.to_numeric(df["position"], errors="coerce").fillna(9999).astype(int)
    df["weeks_on_chart"] = pd.to_numeric(df["weeks_on_chart"], errors="coerce").fillna(9999).astype(int)

    df["artist"] = df["artist"].astype(str).str.strip()
    df["track"] = df["track"].astype(str).str.strip()

    return df


def main() -> None:
    files = sorted(glob.glob(INPUT_GLOB))
    if not files:
        raise FileNotFoundError(f"No CSV files found at: {INPUT_GLOB}")

    rows = []

    for f in files:
        df = pd.read_csv(f, encoding="utf-8-sig")
        df = normalize_columns(df)

        week_date = extract_date_from_filename(f)
        df["week_date"] = week_date  # keep as string for JSON

        # Viral hit approximation: high rank + "recent" chart appearance
        df["viral_hit"] = (df["position"] <= 10) & (df["weeks_on_chart"] <= 4)

        # Keep only viral hits (you can change this if you want all rows with a flag)
        df = df[df["viral_hit"]].copy()

        # Select fields for downstream joins with Ticketmaster
        keep_cols = ["week_date", "artist", "track", "streams", "position", "weeks_on_chart", "viral_hit"]
        if "uri" in df.columns:
            keep_cols.append("uri")

        rows.append(df[keep_cols])

    viral = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(
        columns=["week_date", "artist", "track", "streams", "position", "weeks_on_chart", "viral_hit"]
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(viral.to_dict(orient="records"), indent=2),
        encoding="utf-8"
    )

    print(f"Processed {len(files)} chart CSVs.")
    print(f"Viral rows: {len(viral)}")
    print(f"Saved to: {OUTPUT_PATH}")
    if len(viral) > 0:
        print("\nPreview:")
        print(viral.head(10).to_string(index=False))


if __name__ == "__main__":
    main()