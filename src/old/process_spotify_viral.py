"""Create a processed dataset of Spotify weekly chart tracks.

Input:  data/raw/spotify_charts/*.csv (e.g., regional-global-weekly-YYYY-MM-DD.csv)
Output: data/processed/spotify_charts/spotify_weekly_with_viral_flag.csv
        data/processed/spotify_charts/spotify_weekly_with_viral_flag.json

We keep ALL tracks from the weekly chart CSVs.
We also compute a configurable "viral hit" flag:
- viral_hit: position <= 10 AND weeks_on_chart <= 4
This approximates "high popularity + recent appearance" using chart data.
"""

import glob
import json
import re
from pathlib import Path

import pandas as pd

INPUT_GLOB = "data/raw/spotify_charts/*.csv"

# New outputs that contain ALL rows + a viral_hit flag
OUTPUT_DIR = Path("data/processed/spotify_charts")
OUTPUT_JSON = OUTPUT_DIR / "spotify_weekly_with_viral_flag.json"
OUTPUT_CSV = OUTPUT_DIR / "spotify_weekly_with_viral_flag.csv"


def extract_date_from_filename(path: str) -> str:
    m = re.search(r"\d{4}-\d{2}-\d{2}", path)
    if not m:
        raise ValueError(f"Could not find YYYY-MM-DD in filename: {path}")
    return m.group(0)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names from various export formats to standard names."""
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
    df["streams"] = df["streams"].astype(str).str.replace(",", "", regex=False).str.strip()
    df["streams"] = pd.to_numeric(df["streams"], errors="coerce").fillna(0).astype(int)

    df["position"] = pd.to_numeric(df["position"], errors="coerce").fillna(9999).astype(int)
    df["weeks_on_chart"] = (
        pd.to_numeric(df["weeks_on_chart"], errors="coerce").fillna(9999).astype(int)
    )

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
        df["week_date"] = week_date  # keep as string for JSON/CSV

        # Viral hit approximation: high rank + "recent" chart appearance
        df["viral_hit"] = (df["position"] <= 10) & (df["weeks_on_chart"] <= 4)

        # Keep ALL rows, but include the flag
        keep_cols = [
            "week_date",
            "artist",
            "track",
            "streams",
            "position",
            "weeks_on_chart",
            "viral_hit",
        ]
        if "uri" in df.columns:
            keep_cols.append("uri")

        rows.append(df[keep_cols])

    weekly = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(
        columns=[
            "week_date",
            "artist",
            "track",
            "streams",
            "position",
            "weeks_on_chart",
            "viral_hit",
        ]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save CSV
    weekly.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    # Save JSON
    OUTPUT_JSON.write_text(
        json.dumps(weekly.to_dict(orient="records"), indent=2),
        encoding="utf-8",
    )

    print(f"Processed {len(files)} chart CSVs.")
    print(f"Total rows kept (all tracks): {len(weekly)}")
    if "viral_hit" in weekly.columns:
        print("Viral_hit counts:")
        print(weekly["viral_hit"].value_counts(dropna=False).to_string())
    print(f"Saved CSV to: {OUTPUT_CSV}")
    print(f"Saved JSON to: {OUTPUT_JSON}")

    if len(weekly) > 0:
        print("\nPreview:")
        print(weekly.head(10).to_string(index=False))


if __name__ == "__main__":
    main()