# analyse_geo_align.py  v2  — Listener-gewichtete Geo-Alignment-Analyse
#
# Frage: Wie gut stimmen die Laender mit der hoechsten Last.fm Listener-Reichweite
#        mit den Tour-Laendern auf Ticketmaster ueberein?
#
# Ansatz:
#   Pro Artist: Top-K Laender nach listeners_in_country (nicht nur "ist drin/nicht drin")
#   → Weighted Jaccard: Ueberlappung gewichtet nach Listener-Anteil
#   → Coverage-Metriken auf den Top-K Streaming-Laendern
#
# Input:
#   data/raw/lastfm_geo_presence.csv   (country, artist_name, rank, listeners_in_country)
#   data/processed/f4_city_frequencies.csv
#   data/processed/final_dataset.csv
# Output:
#   data/processed/geo_alignment.csv

import pandas as pd
import numpy as np
from scipy import stats
import os, sys

GEO_FILE = "data/raw/lastfm_geo_presence.csv"
CITY_FILE = "data/processed/f4_city_frequencies.csv"
FINAL_FILE = "data/processed/final_dataset.csv"

for p in [GEO_FILE, CITY_FILE, FINAL_FILE]:
    if not os.path.exists(p):
        print(f"❌ {p} fehlt")
        if p == GEO_FILE:
            print("   → python scripts/collect_lastfm_geo.py")
        sys.exit(1)

geo = pd.read_csv(GEO_FILE)
cities = pd.read_csv(CITY_FILE)
final = pd.read_csv(FINAL_FILE)

# ── Normalisierung ────────────────────────────────────────────────────────
for df in [geo, cities, final]:
    df["artist_norm"] = df[
        "artist_name" if "artist_name" in df.columns else "artist"
    ].str.lower().str.strip()

# listeners_in_country sicherstellen
if "listeners_in_country" not in geo.columns:
    print("⚠️  Spalte 'listeners_in_country' fehlt — collect_lastfm_geo.py neu ausfuehren")
    geo["listeners_in_country"] = 0
geo["listeners_in_country"] = pd.to_numeric(geo["listeners_in_country"], errors="coerce").fillna(0)

# ── Pro Artist: Top-K Streaming-Laender nach Listeners ───────────────────
# K = 10 (konfigurierbar) — Top-10 Laender pro Artist
TOP_K = 10


def top_k_countries(group: pd.DataFrame, k: int = TOP_K) -> dict:
    """
    Gibt die Top-K Laender nach listeners_in_country zurueck,
    inkl. der Listener-Summe und -Anteile.
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

# ── Tour Countries pro Artist ─────────────────────────────────────────────
tour_map = (
    cities.groupby("artist_norm")["country"]
    .apply(set)
    .reset_index()
    .rename(columns={"country": "tour_countries"})
)


# ── Alignment-Metriken ────────────────────────────────────────────────────
def jaccard(a: set, b: set) -> float:
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)


def coverage(inter: set, ref: set) -> float:
    if not ref: return 0.0
    return len(inter) / len(ref)


def weighted_coverage(inter: set, top_df: pd.DataFrame) -> float:
    """
    Gewichtete Tour-Coverage:
    Summe der Listeners in ueberlappenden Laendern / Gesamt-Listeners Top-K
    → Misst ANTEIL der Listener-Reichweite die durch Tour abgedeckt wird.
    """
    total = top_df["listeners_in_country"].sum()
    if total == 0: return 0.0
    covered = top_df[top_df["country"].isin(inter)]["listeners_in_country"].sum()
    return covered / total


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
for c in ["listeners", "jaccard", "tour_coverage", "streaming_reach", "weighted_coverage"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

SEP = "=" * 62

# ══════════════════════════════════════════════════════════════════════════
# A) DESKRIPTIVE STATISTIK
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print(f"A) DESKRIPTIVE STATISTIK — Geo-Alignment  (n={len(df)})")
print(f"   Methode: Top-{TOP_K} Streaming-Laender nach Last.fm Listeners")
print(SEP)

for col, label in [
    ("jaccard", "Jaccard-Similarity (binary)"),
    ("weighted_coverage", "Weighted Coverage  (listener-gewichtet)"),
    ("tour_coverage", "Tour Coverage      (% Tour-Laender gestreamt)"),
    ("streaming_reach", "Streaming Reach    (% Stream-Laender getourt)"),
    ("n_aligned", "Aligned Countries  (Anzahl)"),
    ("n_streaming", "Streaming Countries Top-K"),
    ("n_tour_countries", "Tour Countries"),
]:
    s = df[col]
    print(f"  {label}")
    print(f"    Mittelwert={s.mean():.3f}  Median={s.median():.3f}  "
          f"Std={s.std():.3f}  Min={s.min():.0f}  Max={s.max():.0f}")

# ══════════════════════════════════════════════════════════════════════════
# B) KORRELATION
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("B) KORRELATION — log(Listeners) vs. Alignment-Metriken")
print(SEP)

for metric, label in [
    ("jaccard", "Jaccard"),
    ("weighted_coverage", "Weighted Coverage (Listener-gewichtet)"),
    ("tour_coverage", "Tour Coverage"),
    ("streaming_reach", "Streaming Reach"),
]:
    tmp = df.dropna(subset=["listeners", metric])
    if len(tmp) < 5: continue
    r, p = stats.pearsonr(np.log10(tmp["listeners"] + 1), tmp[metric])
    print(f"  {label:<40} r={r:+.3f}  p={p:.4f}  {'✅' if p < 0.05 else '⚠️'}")

# ══════════════════════════════════════════════════════════════════════════
# C) NACH POPULARITY-TIER
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("C) ALIGNMENT NACH POPULARITY-TIER (Quartile nach Listeners)")
print(SEP)

df_q = df.dropna(subset=["listeners"]).copy()
df_q["tier"] = pd.qcut(df_q["listeners"], q=4,
                       labels=["Q1 (niedrig)", "Q2", "Q3", "Q4 (hoch)"])
grp = df_q.groupby("tier", observed=True)[
    ["jaccard", "weighted_coverage", "tour_coverage", "streaming_reach"]
].mean()
print(grp.round(3).to_string())

kw_groups = [df_q[df_q["tier"] == t]["weighted_coverage"].dropna().values
             for t in df_q["tier"].unique() if len(df_q[df_q["tier"] == t]) > 1]
if len(kw_groups) >= 2:
    h, p_kw = stats.kruskal(*kw_groups)
    print(f"\n  Kruskal-Wallis (Weighted Coverage ~ Tier): H={h:.2f}  p={p_kw:.4f}  "
          f"{'✅' if p_kw < 0.05 else '⚠️'}")

# ══════════════════════════════════════════════════════════════════════════
# D) TOP / BOTTOM
# ══════════════════════════════════════════════════════════════════════════
show_cols = ["artist_name", "listeners", "weighted_coverage", "jaccard",
             "tour_coverage", "streaming_reach", "n_streaming",
             "n_tour_countries", "n_aligned", "top_streaming_country"]
show_cols = [c for c in show_cols if c in df.columns]

print(f"\n{SEP}")
print("D1) TOP 10 — Hoechste Weighted Coverage (Listener-Laender gut getourt)")
print(SEP)
print(df.nlargest(10, "weighted_coverage")[show_cols].to_string(index=False))

print(f"\n{SEP}")
print("D2) BOTTOM 10 — Niedrigste Weighted Coverage (viele Listener-Laender nicht getourt)")
print(SEP)
print(df.nsmallest(10, "weighted_coverage")[show_cols].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# E) SPEICHERN
# ══════════════════════════════════════════════════════════════════════════
df[show_cols].to_csv("data/processed/geo_alignment.csv", index=False)
print(f"\n✅ data/processed/geo_alignment.csv ({len(df)} Artists)")

# ══════════════════════════════════════════════════════════════════════════
# F) ANTWORT
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("F) ANTWORT")
print(SEP)

wc = df["weighted_coverage"].mean()
tc = df["tour_coverage"].mean()
sr = df["streaming_reach"].mean()
jac = df["jaccard"].mean()

print(f"""
Frage: Wie gut stimmen die Laender mit der hoechsten Last.fm Listener-Reichweite
       mit den Tour-Laendern ueberein?

Methode: Top-{TOP_K} Streaming-Laender pro Artist nach listeners_in_country.

  Weighted Coverage:    {wc:.1%}  der Listener-Reichweite wird durch Tour abgedeckt
  Jaccard-Similarity:  {jac:.3f}
  Tour Coverage:       {tc:.1%}  der Tour-Laender sind auch Top-Streaming-Laender
  Streaming Reach:     {sr:.1%}  der Top-Streaming-Laender werden betourt

  → {"Starke Ausrichtung: Artists touren gezielt dorthin wo ihre groesste Hoererschaft ist." if wc > 0.6
else "Moderate Ausrichtung: Streaming-Reichweite und Tour teilweise deckungsgleich." if wc > 0.35
else "Schwache Ausrichtung: Viele Laender mit hoher Listener-Dichte werden nicht betourt."}
""")
