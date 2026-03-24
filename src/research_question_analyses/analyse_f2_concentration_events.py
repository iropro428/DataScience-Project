# =============================================================================
# AI was actively used for the generation and creation of the code.
# =============================================================================

# Standalone Data-Science Analysis for F2:
# Streaming Concentration (Top Track Share) vs. Tour Intensity (Events/Year)
#
# Prerequisite: join_data.py has been executed (requires lastfm_toptracks.csv)
#
# Console Output:
#    A) Descriptive Statistics (Concentration Metrics)
#    B) Top/Bottom Artists
#    C) Track Profile: Extreme Cases
#
# Output Files:
#    data/processed/f2_results.csv

import pandas as pd
import numpy as np
from scipy import stats
import os
import sys

# Loading
FINAL = "data/processed/final_dataset.csv"
TRACKS = "data/raw/lastfm_toptracks.csv"

# Check if the final dataset exists
if not os.path.exists(FINAL):
    print(f" {FINAL} is missing — please run join_data.py first")
    sys.exit(1)

df = pd.read_csv(FINAL)

F2_COLS = ["top5_share", "events_last_year"]
# Check if required columns are in the dataset
missing = [c for c in F2_COLS if c not in df.columns]
if missing:
    print(f" Missing columns: {missing}")
    print("   → Please run collect_toptracks.py + join_data.py")
    sys.exit(1)

# Convert specific columns to numeric values, if applicable
for col in ["top5_share", "top3_share", "top1_share", "hhi", 
            "events_last_year", "total_events", "listeners", 
            "n_tracks", "total_track_plays"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df_f2 = df.dropna(subset=["top5_share", "events_last_year"]).copy()

# Coverage calculation
total_artists = len(df)
f2_artists = len(df_f2)
coverage_pct = f2_artists / total_artists * 100

SEP = "=" * 60
print(f"\n{SEP}")
print(f"F2 ANALYSIS: Streaming Concentration vs. Tour Intensity")
print(f"{SEP}")
print(f"Total artists:         {total_artists}")
print(f"Artists with F2 data:  {f2_artists}  ({coverage_pct:.0f}%)")
print(f"Artists without Toptracks: {total_artists - f2_artists}")

# ══════════════════════════════════════════════════════════════════════════
# A) DESCRIPTIVE STATISTICS
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("A) DESCRIPTIVE STATISTICS — Concentration Metrics")
print(SEP)

conc_cols = [col for col in ["top1_share", "top3_share", "top5_share", "hhi", 
                             "n_tracks", "events_last_year", "total_events"] 
             if col in df_f2.columns]
# Display descriptive statistics for concentration columns
print(df_f2[conc_cols].describe().round(2).to_string())

# Additional concentration distribution analysis
print(f"""
Concentration distribution (top5_share):
  Ø top5_share:    {df_f2['top5_share'].mean():.1f}%
  Median:          {df_f2['top5_share'].median():.1f}%
  Std:             {df_f2['top5_share'].std():.1f}%
  Min → Max:       {df_f2['top5_share'].min():.1f}% → {df_f2['top5_share'].max():.1f}%

  < 40%  (broad profile):          {(df_f2['top5_share'] < 40).sum()} Artists  ({(df_f2['top5_share'] < 40).mean() * 100:.0f}%)
  40–60% (moderate profile):        {((df_f2['top5_share'] >= 40) & (df_f2['top5_share'] < 60)).sum()} Artists
  ≥ 60%  (concentrated profile):   {(df_f2['top5_share'] >= 60).sum()} Artists  ({(df_f2['top5_share'] >= 60).mean() * 100:.0f}%)

Tour Intensity (events_last_year):
  Ø Events/year:   {df_f2['events_last_year'].mean():.1f}
  Median:          {df_f2['events_last_year'].median():.1f}
  Artists with 0 Events/year: {(df_f2['events_last_year'] == 0).sum()}
""")

# ══════════════════════════════════════════════════════════════════════════
# B) TOP / BOTTOM ARTISTS
# ══════════════════════════════════════════════════════════════════════════
cols_show = [col for col in ["artist_name", "top5_share", "top1_share", "hhi", 
                             "events_last_year", "total_events", "listeners"] 
             if col in df_f2.columns]
df_min3 = df_f2[df_f2["events_last_year"] >= 1]

print(f"\n{SEP}")
print("D1) TOP 10 — Highest Streaming Concentration (min. 1 Event/year)")
print(SEP)
print(df_min3.nlargest(10, "top5_share")[cols_show].to_string(index=False))

print(f"\n{SEP}")
print("D2) BOTTOM 10 — Lowest Streaming Concentration (min. 1 Event/year)")
print(SEP)
print(df_min3.nsmallest(10, "top5_share")[cols_show].to_string(index=False))

print(f"\n{SEP}")
print("D3) TOP 10 — Most Tour-Intensive Artists (Events/year)")
print(SEP)
print(df_f2.nlargest(10, "events_last_year")[cols_show].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# C) TRACK PROFILE: Extreme Cases (if Toptracks exists)
# ══════════════════════════════════════════════════════════════════════════
if os.path.exists(TRACKS):
    print(f"\n{SEP}")
    print("E) TRACK PROFILE — Top-3 Most Concentrated and Broad Artists")
    print(SEP)

    df_tracks = pd.read_csv(TRACKS)
    df_tracks["playcount"] = pd.to_numeric(df_tracks["playcount"], errors="coerce")

    extremes = (
            df_min3.nlargest(3, "top5_share")["artist_name"].tolist() +
            df_min3.nsmallest(3, "top5_share")["artist_name"].tolist()
    )

    for artist in extremes:
        row = df_f2[df_f2["artist_name"] == artist]
        if len(row) == 0:
            continue
        row = row.iloc[0]
        tracks = df_tracks[df_tracks["artist_name"] == artist].sort_values("rank").head(5)

        top5 = row["top5_share"]
        ev = row["events_last_year"]
        tag = "🔴 concentrated" if top5 >= 60 else "🟡 moderate" if top5 >= 40 else "🟢 broad"

        print(f"\n  {artist}  [{tag}]")
        print(f"    top5_share = {top5:.1f}%  |  Events/year = {ev:.0f}")

        if len(tracks) > 0:
            total_pc = df_tracks[df_tracks["artist_name"] == artist]["playcount"].sum()
            for _, t in tracks.iterrows():
                pct = t["playcount"] / total_pc * 100 if total_pc > 0 else 0
                bar = "█" * int(pct / 4)
                print(f"    #{int(t['rank']):<2} {str(t['track_name'])[:30]:<30} {pct:>5.1f}%  {bar}")

# ══════════════════════════════════════════════════════════════════════════
# SAVE RESULTS
# ══════════════════════════════════════════════════════════════════════════
result_cols = [col for col in 
               ["artist_name", "top5_share", "top3_share", "top1_share", "hhi", 
                "n_tracks", "total_track_plays", "events_last_year", "total_events", "listeners"]
               if col in df_f2.columns]

df_f2[result_cols].to_csv("data/processed/f2_results.csv", index=False)
print(f"\n\n  data/processed/f2_results.csv saved")
