# analyse_f6_capital_ratio.py
# Standalone Data-Science Analysis for F6: Capital vs. Non-Capital Cities
# No Streamlit — Console Output + CSV
#
# Prerequisite: join_data.py must have been executed
#
# Output:
#   Console — Statistics, Correlations, Rankings
#   data/processed/f6_results.csv

import pandas as pd
import numpy as np
import os, sys

# ══════════════════════════════════════════════════════════════════════════
# Check if required files exist
# ══════════════════════════════════════════════════════════════════════════
for p in ["data/processed/final_dataset.csv",
          "data/processed/f6_capitals_visited.csv",
          "data/processed/f6_capitals_per_artist.csv"]:
    if not os.path.exists(p):
        print(f" {p} is missing — please run join_data.py first")
        sys.exit(1)

df = pd.read_csv("data/processed/final_dataset.csv")
cap_gl = pd.read_csv("data/processed/f6_capitals_visited.csv")
cap_ar = pd.read_csv("data/processed/f6_capitals_per_artist.csv")

# ══════════════════════════════════════════════════════════════════════════
# Ensure necessary columns are present
# ══════════════════════════════════════════════════════════════════════════
F6_COLS = ["capital_events", "non_capital_events", "pct_capital",
           "capital_ratio", "unique_capitals", "unique_non_capitals", "pct_capital_cities"]
missing = [c for c in F6_COLS if c not in df.columns]
if missing:
    print(f" Missing columns: {missing} — please run join_data.py again")
    sys.exit(1)

# Convert relevant columns to numeric types
for c in F6_COLS + ["total_events", "listeners"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Filter rows with missing values in key columns
df_f6 = df.dropna(subset=["capital_events", "non_capital_events"]).copy()

SEP = "=" * 56

# ══════════════════════════════════════════════════════════════════════════
# DESCRIPTIVE STATISTICS
# ══════════════════════════════════════════════════════════════════════════
print(SEP)
print("A) DESCRIPTIVE STATISTICS")
print(SEP)
# Display descriptive statistics for the specified columns
print(df_f6[F6_COLS].describe().round(2).to_string())

# Calculate totals and ratios
total_cap = df_f6["capital_events"].sum()
total_non = df_f6["non_capital_events"].sum()
total_all = total_cap + total_non
glob_pct = total_cap / total_all * 100 if total_all > 0 else 0
glob_ratio = total_cap / total_non if total_non > 0 else float("inf")

print(f"""
Global dataset:
  Capital Events:           {total_cap:.0f}
  Non-Capital Events:       {total_non:.0f}
  % Capital Events:         {glob_pct:.1f}%
  Ratio (cap / non-cap):    {glob_ratio:.3f}

  Ø pct_capital:            {df_f6['pct_capital'].mean():.1f}%
  Median pct_capital:       {df_f6['pct_capital'].median():.1f}%
  Ø unique_capitals:        {df_f6['unique_capitals'].mean():.1f}
  Ø pct_capital_cities:     {df_f6['pct_capital_cities'].mean():.1f}%

  Artists with 0% Capital:   {(df_f6['pct_capital'] == 0).sum()}
  Artists with ≥50% Capital: {(df_f6['pct_capital'] >= 50).sum()}
  Artists with 100% Capital: {(df_f6['pct_capital'] == 100).sum()}
""")

# ══════════════════════════════════════════════════════════════════════════
# TOP / BOTTOM ARTISTS
# ══════════════════════════════════════════════════════════════════════════
cols_show = ["artist_name", "capital_events", "non_capital_events", "pct_capital",
             "unique_capitals", "total_events"]
df_min5 = df_f6[df_f6["total_events"] >= 5]

# Display top 10 artists with highest pct_capital
print(f"\n{SEP}")
print("D) TOP 10 — Highest Capital Share (min. 5 Events)")
print(SEP)
print(df_min5.nlargest(10, "pct_capital")[cols_show].to_string(index=False))

# Display bottom 10 artists with lowest pct_capital
print(f"\n{SEP}")
print("D) BOTTOM 10 — Lowest Capital Share (min. 5 Events)")
print(SEP)
print(df_min5.nsmallest(10, "pct_capital")[cols_show].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# MOST VISITED CAPITALS
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("E) TOP 20 MOST VISITED CAPITALS (all Artists)")
print(SEP)
print(cap_gl.head(20).to_string(index=False))

# Artists per Capital
print(f"\n{SEP}")
print("E2) TOP 10 — Capitals by Number of Different Artists")
print(SEP)
print(cap_gl.nlargest(10, "n_artists")[["city", "country", "n_artists", "total_visits"]].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# SAVE RESULTS
# ══════════════════════════════════════════════════════════════════════════
# Save the results to a CSV file
result_cols = [c for c in
               ["artist_name", "total_events", "capital_events", "non_capital_events",
                "pct_capital", "capital_ratio", "unique_capitals", "unique_non_capitals",
                "pct_capital_cities", "listeners"]
               if c in df_f6.columns]
df_f6[result_cols].to_csv("data/processed/f6_results.csv", index=False)
print(f"\n  data/processed/f6_results.csv saved")
