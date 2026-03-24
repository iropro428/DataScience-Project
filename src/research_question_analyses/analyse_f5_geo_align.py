# analyse_geo_align.py v2 — Listener-weighted Geo-Alignment Analysis
#
# Question: How well do the countries with the highest Last.fm listener reach
#           align with the tour countries of the artists?
#
# Approach:
#   For each artist: Top-K countries based on listeners_in_country (not just "in" or "not in")
#   → Weighted Jaccard: Overlap weighted by listener share
#   → Coverage metrics for the Top-K streaming countries
# 
# Input:
#   data/raw/lastfm_geo_presence.csv   (country, artist_name, rank, listeners_in_country)
#   data/processed/f4_city_frequencies.csv   (city, country, visit frequencies)
#   data/processed/final_dataset.csv   (artist_name, total_events, listeners, etc.)
#
# Output:
#   data/processed/geo_alignment.csv   (artist_name, listeners, tour_coverage, streaming_reach, etc.)

import pandas as pd
import numpy as np
from scipy import stats
import os, sys

GEO_FILE = "data/raw/lastfm_geo_presence.csv"
CITY_FILE = "data/processed/f4_city_frequencies.csv"
FINAL_FILE = "data/processed/final_dataset.csv"

# ══════════════════════════════════════════════════════════════════════════
# Check if required files exist
# ══════════════════════════════════════════════════════════════════════════
for p in [GEO_FILE, CITY_FILE, FINAL_FILE]:
    if not os.path.exists(p):
        print(f"{p} is missing")
        if p == GEO_FILE:
            print("   → Please run python scripts/collect_lastfm_geo.py")
        sys.exit(1)

geo = pd.read_csv(GEO_FILE)
cities = pd.read_csv(CITY_FILE)
final = pd.read_csv(FINAL_FILE)

# ══════════════════════════════════════════════════════════════════════════
# Normalization 
# ══════════════════════════════════════════════════════════════════════════
# Normalize artist names for comparison (lowercase and stripped)
for df in [geo, cities, final]:
    df["artist_norm"] = df[
        "artist_name" if "artist_name" in df.columns else "artist"
    ].str.lower().str.strip()

# Ensure 'listeners_in_country' exists in the geo dataset
if "listeners_in_country" not in geo.columns:
    print(" Column 'listeners_in_country' is missing — please rerun collect_lastfm_geo.py")
    geo["listeners_in_country"] = 0
geo["listeners_in_country"] = pd.to_numeric(geo["listeners_in_country"], errors="coerce").fillna(0)

# ══════════════════════════════════════════════════════════════════════════
# Per Artist: Top-K Streaming Countries by Listeners 
# ══════════════════════════════════════════════════════════════════════════
# K = 10 (configurable) — Top 10 countries per artist
TOP_K = 10

def top_k_countries(group: pd.DataFrame, k: int = TOP_K) -> dict:
    """
    Returns the top-K countries based on listeners_in_country,
    including the total listeners and their share.
    """
    g = group.sort_values("listeners_in_country", ascending=False).head(k)
    total = g["listeners_in_country"].sum()
    return {
        "top_countries": set(g["country"]),
        "top_countries_df": g[["country", "listeners_in_country"]].copy(),
        "total_listeners_top": total,
    }

streaming_data = {}
for artist, group in geo.groupby("artist_norm"):
    streaming_data[artist] = top_k_countries(group, TOP_K)

# ══════════════════════════════════════════════════════════════════════════
# Tour Countries per Artist 
# ══════════════════════════════════════════════════════════════════════════
# Create a map of artist and their tour countries
tour_map = (
    cities.groupby("artist_norm")["country"]
    .apply(set)
    .reset_index()
    .rename(columns={"country": "tour_countries"})
)

# ══════════════════════════════════════════════════════════════════════════
# Alignment Metrics 
# ══════════════════════════════════════════════════════════════════════════
def jaccard(a: set, b: set) -> float:
    """
    Calculate Jaccard similarity between two sets.
    """
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)

def coverage(inter: set, ref: set) -> float:
    """
    Calculate coverage of intersection over reference set.
    """
    if not ref: return 0.0
    return len(inter) / len(ref)

def weighted_coverage(inter: set, top_df: pd.DataFrame) -> float:
    """
    Weighted tour coverage:
    Sum of listeners in overlapping countries / total listeners in top-K countries
    → Measures the share of listeners' reach covered by the tour.
    """
    total = top_df["listeners_in_country"].sum()
    if total == 0: return 0.0
    covered = top_df[top_df["country"].isin(inter)]["listeners_in_country"].sum()
    return covered / total
    
# ══════════════════════════════════════════════════════════════════════════
# Calculate alignment metrics for each artist 
# ══════════════════════════════════════════════════════════════════════════
rows = []
for _, row in final.iterrows():
    norm = row["artist_norm"]
    if norm not in streaming_data: continue

    sd = streaming_data[norm]
    tc_row = tour_map[tour_map["artist_norm"] == norm]
    if tc_row.empty: continue

    sc = sd["top_countries"]  # Streaming countries (Top-K)
    tc = tc_row.iloc[0]["tour_countries"]  # Tour countries

    inter = sc & tc
    rows.append({
        "artist_name": row.get("artist_name", norm),
        "listeners": row.get("listeners"),
        "total_events": row.get("total_events"),
        "jaccard": jaccard(sc, tc),
        "tour_coverage": coverage(inter, tc),
        "streaming_reach": coverage(inter, sc),
        "weighted_coverage": weighted_coverage(inter, sd["top_countries_df"]),
        "n_streaming": len(sc),
        "n_tour_countries": len(tc),
        "n_aligned": len(inter),
        "top_streaming_country": sd["top_countries_df"].iloc[0]["country"] if len(sd["top_countries_df"]) else "",
        "top_streaming_listeners": sd["top_countries_df"].iloc[0]["listeners_in_country"] if len(sd["top_countries_df"]) else 0,
    })

df = pd.DataFrame(rows)
# Convert relevant columns to numeric types
for c in ["listeners", "jaccard", "tour_coverage", "streaming_reach", "weighted_coverage"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

SEP = "=" * 62

# ══════════════════════════════════════════════════════════════════════════
# DESCRIPTIVE STATISTICS
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print(f"A) DESCRIPTIVE STATISTICS — Geo-Alignment  (n={len(df)})")
print(f"   Method: Top-{TOP_K} Streaming Countries by Last.fm Listeners")
print(SEP)

# Display descriptive statistics for the alignment metrics
for col, label in [
    ("jaccard", "Jaccard Similarity (binary)"),
    ("weighted_coverage", "Weighted Coverage  (listener-weighted)"),
    ("tour_coverage", "Tour Coverage      (% Tour Countries streamed)"),
    ("streaming_reach", "Streaming Reach    (% Stream Countries toured)"),
    ("n_aligned", "Aligned Countries  (count)"),
    ("n_streaming", "Streaming Countries Top-K"),
    ("n_tour_countries", "Tour Countries"),
]:
    s = df[col]
    print(f"  {label}")
    print(f"    Mean={s.mean():.3f}  Median={s.median():.3f}  "
          f"Std={s.std():.3f}  Min={s.min():.0f}  Max={s.max():.0f}")

# ══════════════════════════════════════════════════════════════════════════
# TOP / BOTTOM
# ══════════════════════════════════════════════════════════════════════════
show_cols = ["artist_name", "listeners", "weighted_coverage", "jaccard",
             "tour_coverage", "streaming_reach", "n_streaming",
             "n_tour_countries", "n_aligned", "top_streaming_country"]
show_cols = [c for c in show_cols if c in df.columns]

# Display top 10 artists with the highest weighted coverage
print(f"\n{SEP}")
print("D1) TOP 10 — Highest Weighted Coverage (Listener Countries well toured)")
print(SEP)
print(df.nlargest(10, "weighted_coverage")[show_cols].to_string(index=False))

# Display bottom 10 artists with the lowest weighted coverage
print(f"\n{SEP}")
print("D2) BOTTOM 10 — Lowest Weighted Coverage (many Listener Countries not toured)")
print(SEP)
print(df.nsmallest(10, "weighted_coverage")[show_cols].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# SAVE RESULTS
# ══════════════════════════════════════════════════════════════════════════
df[show_cols].to_csv("data/processed/geo_alignment.csv", index=False)
print(f"\n data/processed/geo_alignment.csv ({len(df)} Artists)")
