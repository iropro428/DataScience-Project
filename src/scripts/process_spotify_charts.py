# process_spotify_charts.py
# Verarbeitet Spotify Weekly Chart CSVs → Künstler-Profil-Tabelle
#
# Input:  data/raw/spotify_charts/*.csv
#         (Dateiname muss YYYY-MM-DD enthalten, z.B. regional-global-weekly-2023-02-23.csv)
#
# Output:
#   data/processed/spotify_charts/chart_artists.csv ← Haupt-Output für F3
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
        raise KeyError(f"Fehlende Pflicht-Spalten. Gefunden: {list(df.columns)}")

    # Streams bereinigen
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

    # Kollaborationen aufsplitten: "Artist A, Artist B" → zwei Zeilen
    df["artist"] = df["artist"].astype(str).str.strip()
    df["artist"] = df["artist"].str.split(", ")
    df = df.explode("artist")
    df["artist"] = df["artist"].str.strip()
    df = df[df["artist"] != ""]

    return df


def main():
    files = sorted(glob.glob(INPUT_GLOB))
    if not files:
        print(f"❌  Keine CSV-Dateien gefunden: {INPUT_GLOB}")
        print("    Spotify Chart CSVs nach data/raw/spotify_charts/ kopieren.")
        return

    print(f"📂  {len(files)} Chart-Dateien gefunden")

    all_frames = []
    skipped = 0

    for f in files:
        date_str = extract_date(f)
        # Datumsfilter Feb 2023 – Feb 2026
        if not (DATE_START <= date_str <= DATE_END):
            skipped += 1
            continue
        try:
            df = pd.read_csv(f, encoding="utf-8-sig")
            df = normalize_columns(df)
            df["week_date"] = pd.to_datetime(date_str)
            all_frames.append(df)
        except Exception as e:
            print(f"  ⚠️  {os.path.basename(f)}: {e}")

    if not all_frames:
        print("❌  Keine verwertbaren Daten nach Datumsfilter")
        return

    print(f"✅  {len(all_frames)} Wochen geladen  |  {skipped} außerhalb Zeitraum")

    data = pd.concat(all_frames, ignore_index=True)

    # ── Monatsaggregation ─────────────────────────────────────────────────
    data["month"] = data["week_date"].dt.to_period("M").astype(str)

    monthly = (
        data.groupby(["month", "week_date", "artist"], as_index=False)["streams"]
        .sum()
        .rename(columns={"week_date": "sample_week_date", "streams": "streams_sample_week"})
        .sort_values(["month", "streams_sample_week"], ascending=[True, False])
    )
    monthly["sample_week_date"] = monthly["sample_week_date"].dt.strftime("%Y-%m-%d")

    # ── Künstler-Profil-Tabelle (für F3 Join) ────────────────────────────
    #  Pro Artist: Summe Streams, Anzahl Wochen im Chart, Spitzenposition, Peak-Monat
    agg = {"streams": "sum", "week_date": "count"}
    if "position" in data.columns:
        agg["position"] = "min"  # beste (=niedrigste) Position

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
    # Zeitraum des ersten / letzten Chartauftritts
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

    print(f"\n✅  {len(artist_profile)} Chart-Künstler → {OUTPUT_ARTISTS}")
    print(f"✅  Monatsdaten            → {OUTPUT_MONTHLY}")

    print(f"\n--- Schnellcheck ---")
    print(f"  Zeitraum:        {data['week_date'].min().date()} – {data['week_date'].max().date()}")
    print(f"  Chart-Wochen:    {data['week_date'].nunique()}")
    print(f"  Chart-Künstler:  {len(artist_profile)}")
    print(f"\nTop 10 Künstler nach Gesamt-Streams:")
    print(artist_profile.head(10)[["artist", "total_chart_streams", "chart_weeks", "peak_position"]].to_string(index=False))


if __name__ == "__main__":
    main()
