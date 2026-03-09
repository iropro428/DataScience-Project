import glob
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, pearsonr, ttest_ind

# -----------------------------
# Paths
# -----------------------------
LASTFM_PATH = "data/raw/artists_lastfm.csv"
SPOTIFY_GLOB = "data/raw/spotify_charts/*.csv"

PLOTS_DIR = Path("data/plots/rq3")
PROCESSED_DIR = Path("data/processed")


# -----------------------------
# Helpers
# -----------------------------
def normalize_name(x: str) -> str:
    return str(x).strip().lower()


def normalize_chart_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {}

    for c in df.columns:
        cc = c.strip().lower()

        if cc in {"artist", "artist_names", "artists"}:
            col_map[c] = "artist"
        elif cc in {"track", "track_name", "track name"}:
            col_map[c] = "track"
        elif cc in {"streams", "stream"}:
            col_map[c] = "streams"
        elif cc in {"position", "rank"}:
            col_map[c] = "position"

    df = df.rename(columns=col_map)

    required = {"artist", "streams", "position"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns {missing}. Found: {list(df.columns)}")

    df["streams"] = pd.to_numeric(
        df["streams"].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )
    df["position"] = pd.to_numeric(df["position"], errors="coerce")

    # split collaborations
    df["artist"] = df["artist"].astype(str).str.split(",")
    df = df.explode("artist")
    df["artist"] = df["artist"].astype(str).str.strip()

    return df


def extract_date(path: str) -> str:
    m = re.search(r"\d{4}-\d{2}-\d{2}", path)
    if not m:
        raise ValueError(f"Could not find date in filename: {path}")
    return m.group(0)


def load_chart_data() -> pd.DataFrame:
    files = sorted(glob.glob(SPOTIFY_GLOB))
    if not files:
        raise FileNotFoundError(f"No Spotify chart CSV files found at {SPOTIFY_GLOB}")

    frames = []
    for fp in files:
        df = pd.read_csv(fp)
        df = normalize_chart_columns(df)
        df["week_date"] = extract_date(fp)
        frames.append(df[["week_date", "artist", "streams", "position"]])

    charts = pd.concat(frames, ignore_index=True)
    charts["artist_norm"] = charts["artist"].map(normalize_name)
    return charts


def cohen_d(x: pd.Series, y: pd.Series) -> float:
    x = x.dropna().to_numpy(dtype=float)
    y = y.dropna().to_numpy(dtype=float)

    if len(x) < 2 or len(y) < 2:
        return np.nan

    nx, ny = len(x), len(y)
    pooled = np.sqrt(
        ((nx - 1) * np.var(x, ddof=1) + (ny - 1) * np.var(y, ddof=1)) / (nx + ny - 2)
    )

    if pooled == 0:
        return 0.0

    return (np.mean(x) - np.mean(y)) / pooled


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Load Last.fm
    lastfm = pd.read_csv(LASTFM_PATH)

    if "name" not in lastfm.columns:
        raise ValueError(f"Expected column 'name' in {LASTFM_PATH}, got {list(lastfm.columns)}")
    if "listeners" not in lastfm.columns:
        raise ValueError(f"Expected column 'listeners' in {LASTFM_PATH}, got {list(lastfm.columns)}")

    lastfm = lastfm.copy()
    lastfm["artist"] = lastfm["name"].astype(str).str.strip()
    lastfm["artist_norm"] = lastfm["artist"].map(normalize_name)
    lastfm["listeners"] = pd.to_numeric(lastfm["listeners"], errors="coerce")

    # Load Spotify weekly chart data
    charts = load_chart_data()

    # Artist-level chart summary
    chart_summary = (
        charts.groupby("artist_norm")
        .agg(
            chart_weeks=("week_date", "nunique"),
            total_streams=("streams", "sum"),
            best_position=("position", "min"),
        )
        .reset_index()
    )
    chart_summary["in_chart"] = True

    # Merge with Last.fm
    df = lastfm.merge(chart_summary, on="artist_norm", how="left")
    df["in_chart"] = df["in_chart"].fillna(False).astype(bool)
    df["chart_weeks"] = df["chart_weeks"].fillna(0)
    df["total_streams"] = df["total_streams"].fillna(0)

    # Split groups
    chart_group = df.loc[df["in_chart"], "listeners"].dropna()
    non_chart_group = df.loc[~df["in_chart"], "listeners"].dropna()

    # -----------------------------
    # Stats
    # -----------------------------
    mw = mannwhitneyu(chart_group, non_chart_group, alternative="two-sided")

    log_chart = np.log10(chart_group)
    log_non = np.log10(non_chart_group)

    welch = ttest_ind(log_chart, log_non, equal_var=False, nan_policy="omit")
    d = cohen_d(log_chart, log_non)

    mean_ratio = chart_group.mean() / non_chart_group.mean()
    median_ratio = chart_group.median() / non_chart_group.median()

    # -----------------------------
    # Graph 1 — Boxplot
    # -----------------------------
    plt.figure(figsize=(10, 6))

    groups = [non_chart_group, chart_group]
    positions = [0, 1]

    plt.boxplot(
        groups,
        vert=False,
        positions=positions,
        tick_labels=["Not in Charts", "In Spotify Charts"],
        patch_artist=True,
        showfliers=False,
        boxprops=dict(facecolor="#2d3a5a", alpha=0.35, edgecolor="#c7d2e3", linewidth=2),
        medianprops=dict(color="#c7d2e3", linewidth=2),
        whiskerprops=dict(color="#9fb2d0", linewidth=1.8),
        capprops=dict(color="#9fb2d0", linewidth=1.8),
    )

    rng = np.random.default_rng(42)
    plt.scatter(
        non_chart_group,
        np.full_like(non_chart_group, 0, dtype=float) + rng.uniform(-0.05, 0.05, size=len(non_chart_group)),
        alpha=0.45,
        s=18,
        label="Not in Charts",
    )
    plt.scatter(
        chart_group,
        np.full_like(chart_group, 1, dtype=float) + rng.uniform(-0.05, 0.05, size=len(chart_group)),
        alpha=0.45,
        s=18,
        label="In Spotify Charts",
    )

    plt.xlabel("Last.fm listeners")
    plt.title("Last.fm listeners — Chart vs. Non-Chart Artists")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "f3_boxplot_chart_vs_nonchart.png", dpi=200)
    plt.close()

    # -----------------------------
    # Graph 2 — Overlay histogram
    # -----------------------------
    plt.figure(figsize=(10, 6))

    bins = 30
    plt.hist(non_chart_group, bins=bins, density=True, alpha=0.45, label="Not in Charts")
    plt.hist(chart_group, bins=bins, density=True, alpha=0.45, label="In Spotify Charts")

    plt.xlabel("Last.fm listeners")
    plt.ylabel("Density")
    plt.title("Listener Distribution — Chart vs. Non‑Chart")
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "f3_hist_overlay_chart_vs_nonchart.png", dpi=200)
    plt.close()

    # -----------------------------
    # Graph 3 — Chart intensity vs listeners
    # -----------------------------
    chart_only = df[
        df["in_chart"] &
        (df["chart_weeks"] > 0) &
        df["listeners"].notna()
    ].copy()

    chart_only["log_listeners"] = np.log10(chart_only["listeners"])
    chart_only["log_chart_weeks"] = np.log10(chart_only["chart_weeks"])
    chart_only["log_total_streams"] = np.where(
        chart_only["total_streams"] > 0,
        np.log10(chart_only["total_streams"]),
        np.nan
    )

    r_weeks, p_weeks = pearsonr(chart_only["log_chart_weeks"], chart_only["log_listeners"])

    valid_streams = chart_only["log_total_streams"].notna()
    r_streams, p_streams = pearsonr(
        chart_only.loc[valid_streams, "log_total_streams"],
        chart_only.loc[valid_streams, "log_listeners"],
    )

    x = chart_only["log_chart_weeks"].to_numpy()
    y = chart_only["log_listeners"].to_numpy()
    m, b = np.polyfit(x, y, 1)
    xx = np.linspace(x.min(), x.max(), 100)

    plt.figure(figsize=(10, 6))
    plt.scatter(
        chart_only["log_chart_weeks"],
        chart_only["log_listeners"],
        c=chart_only["log_listeners"],
        s=60,
        alpha=0.85
    )
    plt.plot(xx, m * xx + b, color="orange", linewidth=2.5, label="OLS")

    plt.xlabel("log10(Chart Weeks)")
    plt.ylabel("log10(Last.fm listeners)")
    plt.title(f"Chart-Intensity vs. Listeners | r = {r_weeks:.3f} | n = {len(chart_only)}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "f3_scatter_chart_intensity_vs_listeners.png", dpi=200)
    plt.close()

    # -----------------------------
    # Save result tables
    # -----------------------------
    results = pd.DataFrame([
        {"metric": "n_total_artists", "value": len(df)},
        {"metric": "n_chart_artists", "value": int(df["in_chart"].sum())},
        {"metric": "n_non_chart_artists", "value": int((~df["in_chart"]).sum())},
        {"metric": "mean_listeners_chart", "value": chart_group.mean()},
        {"metric": "mean_listeners_non_chart", "value": non_chart_group.mean()},
        {"metric": "median_listeners_chart", "value": chart_group.median()},
        {"metric": "median_listeners_non_chart", "value": non_chart_group.median()},
        {"metric": "mean_ratio_chart_vs_non_chart", "value": mean_ratio},
        {"metric": "median_ratio_chart_vs_non_chart", "value": median_ratio},
        {"metric": "mann_whitney_u", "value": mw.statistic},
        {"metric": "mann_whitney_p", "value": mw.pvalue},
        {"metric": "welch_t_log", "value": welch.statistic},
        {"metric": "welch_p_log", "value": welch.pvalue},
        {"metric": "cohens_d_log", "value": d},
        {"metric": "pearson_r_log_chart_weeks_vs_log_listeners", "value": r_weeks},
        {"metric": "pearson_p_log_chart_weeks_vs_log_listeners", "value": p_weeks},
        {"metric": "pearson_r_log_total_streams_vs_log_listeners", "value": r_streams},
        {"metric": "pearson_p_log_total_streams_vs_log_listeners", "value": p_streams},
    ])
    results.to_csv(PROCESSED_DIR / "f3_results.csv", index=False)

    chart_only[
        [
            "artist",
            "listeners",
            "chart_weeks",
            "total_streams",
            "best_position",
            "log_listeners",
            "log_chart_weeks",
            "log_total_streams",
        ]
    ].to_csv(PROCESSED_DIR / "f3_chart_artists_detail.csv", index=False)

    df[
        ["artist", "listeners", "in_chart", "chart_weeks", "total_streams", "best_position"]
    ].to_csv(PROCESSED_DIR / "f3_artist_level_dataset.csv", index=False)

    # -----------------------------
    # Console summary
    # -----------------------------
    print("Saved plots:")
    print("-", PLOTS_DIR / "f3_boxplot_chart_vs_nonchart.png")
    print("-", PLOTS_DIR / "f3_hist_overlay_chart_vs_nonchart.png")
    print("-", PLOTS_DIR / "f3_scatter_chart_intensity_vs_listeners.png")
    print("-")
    print("Saved tables:")
    print("-", PROCESSED_DIR / "f3_results.csv")
    print("-", PROCESSED_DIR / "f3_chart_artists_detail.csv")
    print("-", PROCESSED_DIR / "f3_artist_level_dataset.csv")
    print()

    print(f"Welch t-test (log) = {welch.statistic:.3f} | p = {welch.pvalue:.4g}")
    print(f"Cohen's d (log) = {d:.3f}")
    print(f"Chart artists have mean {mean_ratio:.2f}x listeners and median {median_ratio:.2f}x listeners.")
    print(f"Chart weeks vs listeners: r = {r_weeks:.3f} | p = {p_weeks:.4g}")
    print(f"Total streams vs listeners: r = {r_streams:.3f} | p = {p_streams:.4g}")


if __name__ == "__main__":
    main()