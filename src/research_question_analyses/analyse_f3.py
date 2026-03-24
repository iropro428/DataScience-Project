# analyse_f3.py
# Standalone Analysis for F3:
# Last.fm Listeners — Chart Artists vs. Non-Chart Artists (Spotify Weekly 2023–2026)
#
# Prerequisites:
#   1. python scripts/process_spotify_charts.py
#   2. python scripts/join_data.py
#      (or directly: run join_f3.py to add 'was_on_chart' flag)
#
# Console Output + data/processed/f3_results.csv

import pandas as pd
import numpy as np
import os, sys

FINAL  = "data/processed/final_dataset.csv"
CHARTS = "data/processed/spotify_charts/chart_artists.csv"

# Check if the required files exist
for p in [FINAL, CHARTS]:
    if not os.path.exists(p):
        print(f" {p} is missing")
        if p == CHARTS:
            print("   → Please run python scripts/process_spotify_charts.py")
        sys.exit(1)

df     = pd.read_csv(FINAL)
charts = pd.read_csv(CHARTS)

# Join: was_on_chart Flag 
# Normalized artist name comparison (lowercase, stripped)
charts["artist_norm"] = charts["artist"].str.lower().str.strip()
df["artist_norm"]     = df["artist_name"].str.lower().str.strip()

# Creating a set of chart artists
chart_set    = set(charts["artist_norm"])
# Mark if an artist is on the chart
df["was_on_chart"] = df["artist_norm"].isin(chart_set)

# Optional chart metrics to join
chart_cols = ["artist_norm","total_chart_streams","chart_weeks","peak_position",
              "first_chart_date","last_chart_date"]
chart_cols = [c for c in chart_cols if c in charts.columns]
df = df.merge(charts[chart_cols], on="artist_norm", how="left")
df.drop(columns=["artist_norm"], inplace=True)

# Convert certain columns to numeric values
for c in ["listeners","playcount","total_events","events_last_year"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Separator for the output
SEP = "=" * 60
n_chart     = df["was_on_chart"].sum()
n_non_chart = (~df["was_on_chart"]).sum()
n_total     = len(df)

# Output general statistics
print(f"\n{SEP}")
print(f"F3 ANALYSIS: Chart Artists vs. Non-Chart Artists")
print(f"{SEP}")
print(f"Total artists:          {n_total}")
print(f"In Spotify Chart:       {n_chart}  ({n_chart/n_total*100:.0f}%)")
print(f"Not in Chart:           {n_non_chart}  ({n_non_chart/n_total*100:.0f}%)")

# ══════════════════════════════════════════════════════════════════════════
# DESCRIPTIVE STATISTICS
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("A) DESCRIPTIVE STATISTICS — Last.fm Listeners")
print(SEP)

# Descriptive statistics for chart vs non-chart artists
for label, mask in [("Chart Artists", df["was_on_chart"]),
                    ("Non-Chart Artists", ~df["was_on_chart"])]:
    sub = df[mask]["listeners"].dropna()
    if len(sub) == 0: continue
    print(f"\n  {label} (n={len(sub)}):")
    print(f"    Mean:          {sub.mean():>15,.0f}")
    print(f"    Median:        {sub.median():>15,.0f}")
    print(f"    Std:           {sub.std():>15,.0f}")
    print(f"    Min:           {sub.min():>15,.0f}")
    print(f"    Max:           {sub.max():>15,.0f}")
    print(f"    Q25:           {sub.quantile(.25):>15,.0f}")
    print(f"    Q75:           {sub.quantile(.75):>15,.0f}")

# Compare the mean listeners between chart and non-chart artists
mean_c  = df[df["was_on_chart"]]["listeners"].mean()
mean_nc = df[~df["was_on_chart"]]["listeners"].mean()
if mean_nc and mean_nc > 0:
    print(f"\n  → Chart Artists have Ø {mean_c/mean_nc:.1f}× more Listeners than Non-Chart Artists")

# ══════════════════════════════════════════════════════════════════════════
#TOP / BOTTOM
# ══════════════════════════════════════════════════════════════════════════
show_cols = [c for c in ["artist_name","was_on_chart","listeners","chart_weeks",
                          "total_chart_streams","peak_position","total_events"]
             if c in df.columns]

# Display top 10 chart artists by listeners
print(f"\n{SEP}")
print("E1) TOP 10 Chart Artists by Last.fm Listeners")
print(SEP)
print(df[df["was_on_chart"]].nlargest(10, "listeners")[show_cols].to_string(index=False))

# Display top 10 non-chart artists by listeners
print(f"\n{SEP}")
print("E2) TOP 10 Non-Chart Artists by Last.fm Listeners")
print(SEP)
print(df[~df["was_on_chart"]].nlargest(10, "listeners")[show_cols].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# SAVE RESULTS
# ══════════════════════════════════════════════════════════════════════════
save_cols = [c for c in ["artist_name","was_on_chart","listeners","playcount",
                          "total_events","events_last_year","total_chart_streams",
                          "chart_weeks","peak_position","first_chart_date","last_chart_date"]
             if c in df.columns]
df[save_cols].to_csv("data/processed/f3_results.csv", index=False)
print(f"\n  data/processed/f3_results.csv saved")
