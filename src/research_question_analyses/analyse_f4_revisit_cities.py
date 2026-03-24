"""
Standalone Data-Science Analysis for F4: Revisit vs. New Cities
Executable without Streamlit — outputs statistics in the console

Prerequisite: join_data.py must have been executed

Console Output:
  - Descriptive Statistics
  - Correlation Analysis
  - Group Comparison (Tour Size)
  - Top/Bottom Artists
  - Most Visited Cities

Output Files:
  data/processed/f4_results.csv
"""

import pandas as pd
import numpy as np
import os, sys

# ══════════════════════════════════════════════════════════════════════════
# Loading
# ══════════════════════════════════════════════════════════════════════════
for p in ["data/processed/final_dataset.csv", "data/processed/f4_city_frequencies.csv"]:
    if not os.path.exists(p):
        print(f" {p} is missing — please run join_data.py first")
        sys.exit(1)

df = pd.read_csv("data/processed/final_dataset.csv")
city_df = pd.read_csv("data/processed/f4_city_frequencies.csv")

F4_COLS = ["revisit_cities", "new_cities", "pct_revisit_cities", "revisit_ratio", "pct_events_revisit"]
missing = [c for c in F4_COLS if c not in df.columns]
if missing:
    print(f" Missing columns: {missing} — please run join_data.py again")
    sys.exit(1)

# Convert columns to numeric values
for col in F4_COLS + ["total_events"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Filter the dataset to remove rows with missing values for the key columns
df_f4 = df.dropna(subset=["revisit_cities", "new_cities"]).copy()
print(f"Artists with F4 data: {len(df_f4)}\n")

SEP = "=" * 56

# ══════════════════════════════════════════════════════════════════════════
# DESCRIPTIVE STATISTICS
# ══════════════════════════════════════════════════════════════════════════
print(SEP)
print("A) DESCRIPTIVE STATISTICS")
print(SEP)
# Display descriptive statistics for the specified columns
print(df_f4[F4_COLS].describe().round(2).to_string())

# Calculate the global statistics for revisit and new cities
total_rev = df_f4["revisit_cities"].sum()
total_new = df_f4["new_cities"].sum()
total_all = total_rev + total_new
glob_ratio = total_rev / total_new if total_new > 0 else float("inf")
glob_pct = total_rev / total_all * 100 if total_all > 0 else 0

print(f"""
Global dataset:
  Revisit Cities:           {total_rev:.0f}
  New Cities:               {total_new:.0f}
  Ratio (revisit / new):    {glob_ratio:.3f}
  % Revisit (Cities):       {glob_pct:.1f}%
  Ø pct_revisit_cities:     {df_f4['pct_revisit_cities'].mean():.1f}%
  Median pct_revisit:       {df_f4['pct_revisit_cities'].median():.1f}%
  Ø pct_events_revisit:     {df_f4['pct_events_revisit'].mean():.1f}%
""")

# ══════════════════════════════════════════════════════════════════════════
# GROUP COMPARISON — Tour Size
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("C) GROUP COMPARISON — pct_revisit_cities by Tour Size (Quartiles)")
print(SEP)

# Categorize artists based on their total events into quartiles
df_f4["tour_q"] = pd.qcut(
    df_f4["total_events"], q=4,
    labels=["Q1 Small", "Q2 Medium", "Q3 Large", "Q4 Very large"],
    duplicates="drop"
)
# Group by the quartiles and calculate descriptive statistics
grp = df_f4.groupby("tour_q", observed=True)["pct_revisit_cities"].agg(
    ["mean", "median", "std", "count"]
).round(2)
print(grp.to_string())

# ══════════════════════════════════════════════════════════════════════════
# TOP / BOTTOM ARTISTS
# ══════════════════════════════════════════════════════════════════════════
cols_show = ["artist_name", "revisit_cities", "new_cities",
             "pct_revisit_cities", "revisit_ratio", "total_events"]

# Filter the data for artists with at least 5 events
df_min5 = df_f4[df_f4["total_events"] >= 5]

# Display top 10 artists with the highest revisit rate
print(f"\n{SEP}")
print("D) TOP 10 — Highest Revisit Rate (min. 5 Events)")
print(SEP)
print(df_min5.nlargest(10, "pct_revisit_cities")[cols_show].to_string(index=False))

# Display bottom 10 artists with the lowest revisit rate
print(f"\n{SEP}")
print("D) BOTTOM 10 — Lowest Revisit Rate (min. 5 Events)")
print(SEP)
print(df_min5.nsmallest(10, "pct_revisit_cities")[cols_show].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# MOST VISITED CITIES
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("E) TOP 20 MOST VISITED CITIES (all Artists)")
print(SEP)

# Summarize city visits
top_cities = (
    city_df.groupby(["city", "country"])["visits"]
    .sum().sort_values(ascending=False).head(20).reset_index()
)
print(top_cities.to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# SAVE RESULTS
# ══════════════════════════════════════════════════════════════════════════
result_cols = [c for c in
               ["artist_name", "total_events", "revisit_cities", "new_cities",
                "pct_revisit_cities", "revisit_ratio", "pct_events_revisit",
                "most_visited_city", "most_visited_n", "listeners"]
               if c in df_f4.columns]

# Save the selected results to a CSV file
df_f4[result_cols].to_csv("data/processed/f4_results.csv", index=False)
print(f"\n  data/processed/f4_results.csv saved")
