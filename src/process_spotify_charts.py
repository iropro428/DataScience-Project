import pandas as pd
import glob
import re
import json
from pathlib import Path


INPUT_PATH = "data/raw/spotify_charts/*.csv"
OUTPUT_FILE = "data/processed/spotify_charts/spotify_artist_streams_monthly.json"


def normalize_columns(df):
    """
    Normalize column names from different Spotify chart formats.
    """

    col_map = {}

    for c in df.columns:
        name = c.strip().lower()

        if name in ["artist", "artist_names", "artists"]:
            col_map[c] = "artist"

        elif name in ["track", "track_name", "track name"]:
            col_map[c] = "track"

        elif name in ["streams"]:
            col_map[c] = "streams"

        elif name in ["position", "rank"]:
            col_map[c] = "position"

        elif name in ["uri", "url"]:
            col_map[c] = "url"

    df = df.rename(columns=col_map)

    required = {"artist", "streams"}
    missing = required - set(df.columns)

    if missing:
        raise KeyError(
            f"Missing required columns {missing}. Found: {list(df.columns)}"
        )

    # Convert streams to numeric
    df["streams"] = (
        df["streams"]
        .astype(str)
        .str.replace(",", "")
    )
    
    # Split artists for collaborated songs
    df["artist"] = df["artist"].str.split(", ")
    df = df.explode("artist")

    df["streams"] = pd.to_numeric(df["streams"], errors="coerce").fillna(0)

    return df


def extract_date(filename):
    """
    Extract date from filename like:
    regional-global-weekly-2023-02-23.csv
    """

    match = re.search(r"\d{4}-\d{2}-\d{2}", filename)

    if not match:
        raise ValueError(f"No date found in filename {filename}")

    return match.group(0)


def main():

    files = sorted(glob.glob(INPUT_PATH))

    if not files:
        raise FileNotFoundError("No Spotify chart CSV files found.")

    all_frames = []

    for file in files:

        df = pd.read_csv(file)

        df = normalize_columns(df)

        date_str = extract_date(file)

        df["date"] = pd.to_datetime(date_str)

        all_frames.append(df[["date", "artist", "streams"]])

    data = pd.concat(all_frames, ignore_index=True)

    # Month label
    data["month"] = data["date"].dt.to_period("M").astype(str)

    # Sample week aggregation
    artist_monthly_sample = (
        data.groupby(["month", "date", "artist"], as_index=False)["streams"]
        .sum()
        .rename(columns={
            "date": "sample_week_date",
            "streams": "streams_sample_week"
        })
        .sort_values(["month", "streams_sample_week"], ascending=[True, False])
    )

    # Convert timestamp to string for JSON
    artist_monthly_sample["sample_week_date"] = (
        artist_monthly_sample["sample_week_date"]
        .dt.strftime("%Y-%m-%d")
    )

    Path("data/processed").mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(
            artist_monthly_sample.to_dict(orient="records"),
            f,
            indent=2
        )

    print(f"\nProcessed {len(files)} Spotify chart CSV files.")
    print(f"Saved dataset to: {OUTPUT_FILE}")

    print("\nPreview:")
    print(artist_monthly_sample.head(10))


if __name__ == "__main__":
    main()