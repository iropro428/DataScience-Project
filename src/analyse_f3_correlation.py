import os
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Config / Paths
CHARTS_PATH = "data/processed/spotify_charts/spotify_weekly_with_viral_flag.json"
LASTFM_PATH = "data/artists_lastfm.csv"

OUT_DIR = "data"
PLOT_DIR = "data/plots"

OUT_SUMMARY_CSV = "rq3_listeners_chart_vs_nonchart_summary.csv"
OUT_MERGED_CSV = "rq3_lastfm_with_chart_flag.csv"  
OUT_PLOT_PNG = "rq3_listeners_chart_vs_nonchart_boxplot.png"



# Helpers
def ensure_exists(path_str: str) -> None:
    p = Path(path_str)
    if not p.exists():
        raise FileNotFoundError(
            f"File not found: {path_str}\n"
            f"Tip: Check your project root and path. Current working dir is: {Path.cwd()}"
        )


def norm_name(x) -> str:
    """Normalize artist names for matching (strip + lower)."""
    return str(x).strip().lower()


def parse_listeners(series: pd.Series) -> pd.Series:
    """Parse listener counts into numeric.

    Handles:
    - plain ints/floats
    - strings with commas: '1,234,567'
    - strings with spaces

    If your data has '1.2M'/'450K', tell me and we can extend this.
    """
    s = series.astype(str).str.replace(",", "", regex=False).str.replace(" ", "", regex=False)
    return pd.to_numeric(s, errors="coerce")


# Main
def main() -> None:
    # Create output folders
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(PLOT_DIR, exist_ok=True)

    # Verify inputs exist
    ensure_exists(CHARTS_PATH)
    ensure_exists(LASTFM_PATH)

    # Load data
    charts = pd.read_json(CHARTS_PATH)
    lastfm = pd.read_csv(LASTFM_PATH)

    # Basic schema checks
    if "artist" not in charts.columns:
        raise ValueError(f"Expected column 'artist' in charts JSON, got: {list(charts.columns)}")
    # Accept either 'artist' or 'name' for the artist column in the Last.fm CSV
    if "artist" in lastfm.columns:
        lastfm_artist_col = "artist"
    elif "name" in lastfm.columns:
        lastfm_artist_col = "name"
    else:
        raise ValueError(
            "Expected an artist column in lastfm CSV ('artist' or 'name'), got: "
            f"{list(lastfm.columns)}"
        )
    if "listeners" not in lastfm.columns:
        raise ValueError(f"Expected column 'listeners' in lastfm CSV, got: {list(lastfm.columns)}")

    # Clean & explode artist names in charts (handle collaborations like 'A, B')
    charts = charts.copy()
    charts["artist"] = charts["artist"].astype(str).str.split(",")
    charts = charts.explode("artist")
    charts["artist"] = charts["artist"].astype(str).str.strip()
    charts = charts[charts["artist"].notna() & (charts["artist"] != "")]

    # Normalize names for robust matching
    charts["artist_norm"] = charts["artist"].map(norm_name)
    lastfm = lastfm.copy()
    lastfm["artist_norm"] = lastfm[lastfm_artist_col].map(norm_name)

    chart_artists = set(charts["artist_norm"].unique())

    # Add chart flag
    lastfm["in_charts"] = lastfm["artist_norm"].isin(chart_artists)

    # Parse listeners as numeric
    lastfm["listeners"] = parse_listeners(lastfm["listeners"])

    # Debug / sanity outputs
    total_artists = len(lastfm)
    matched = int(lastfm["in_charts"].sum())
    match_rate = float(lastfm["in_charts"].mean()) if total_artists else 0.0

    print("\n=== RQ3: Last.fm listeners: chart vs non-chart artists ===")
    print(f"Total Last.fm artists: {total_artists}")
    print(f"Matched chart artists: {matched}")
    print(f"Match rate: {match_rate:.2%}")
    print(f"Last.fm artist column used: {lastfm_artist_col}")

    # Summary stats
    summary = (
        lastfm.groupby("in_charts")["listeners"]
        .agg(["count", "mean", "median"])
        .reset_index()
    )

    print("\nSummary (listeners):")
    print(summary)

    # Save outputs
    summary_path = os.path.join(OUT_DIR, OUT_SUMMARY_CSV)
    merged_path = os.path.join(OUT_DIR, OUT_MERGED_CSV)
    plot_path = os.path.join(PLOT_DIR, OUT_PLOT_PNG)

    summary.to_csv(summary_path, index=False)
    lastfm.to_csv(merged_path, index=False)

    # Plot (filter >0 for log-scale stability)
    chart_listeners = lastfm.loc[lastfm["in_charts"], "listeners"].dropna()
    nonchart_listeners = lastfm.loc[~lastfm["in_charts"], "listeners"].dropna()

    chart_listeners = chart_listeners[chart_listeners > 0]
    nonchart_listeners = nonchart_listeners[nonchart_listeners > 0]

    plt.figure()
    plt.boxplot([nonchart_listeners, chart_listeners], labels=["Not in Charts", "In Charts"])
    plt.yscale("log")
    plt.title("Last.fm listeners: Chart vs Non-Chart Artists")
    plt.ylabel("Listeners (log scale)")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=200)
    plt.close()

    print(f"\nSaved summary CSV to: {summary_path}")
    print(f"Saved merged CSV to: {merged_path}")
    print(f"Saved plot to: {plot_path}")


if __name__ == "__main__":
    main()
