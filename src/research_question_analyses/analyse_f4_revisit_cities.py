# Standalone Data-Science Analyse für F4: Revisit vs. New Cities
# Ausführbar ohne Streamlit — gibt Statistiken in der Console aus
#
# Voraussetzung: join_data.py wurde ausgeführt
#
# Output Console:
#   - Deskriptive Statistik
#   - Korrelationsanalyse
#   - Gruppenvergleich (Tour-Größe)
#   - Top/Bottom Artists
#   - Meistbesuchte Städte
#
# Output Dateien:
#   data/processed/f4_results.csv

import pandas as pd
import numpy as np
from scipy import stats
import os, sys

# ── Laden ──────────────────────────────────────────────────────────────────
for p in ["data/processed/final_dataset.csv", "data/processed/f4_city_frequencies.csv"]:
    if not os.path.exists(p):
        print(f"❌  {p} fehlt — erst join_data.py ausführen")
        sys.exit(1)

df = pd.read_csv("data/processed/final_dataset.csv")
city_df = pd.read_csv("data/processed/f4_city_frequencies.csv")

F4_COLS = ["revisit_cities", "new_cities", "pct_revisit_cities", "revisit_ratio", "pct_events_revisit"]
missing = [c for c in F4_COLS if c not in df.columns]
if missing:
    print(f"❌  Fehlende Spalten: {missing} — join_data.py erneut ausführen")
    sys.exit(1)

for col in F4_COLS + ["total_events"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df_f4 = df.dropna(subset=["revisit_cities", "new_cities"]).copy()
print(f"Artists mit F4-Daten: {len(df_f4)}\n")

SEP = "=" * 56

# ══════════════════════════════════════════════════════════════════════════
# A) DESKRIPTIVE STATISTIK
# ══════════════════════════════════════════════════════════════════════════
print(SEP)
print("A) DESKRIPTIVE STATISTIK")
print(SEP)
print(df_f4[F4_COLS].describe().round(2).to_string())

total_rev = df_f4["revisit_cities"].sum()
total_new = df_f4["new_cities"].sum()
total_all = total_rev + total_new
glob_ratio = total_rev / total_new if total_new > 0 else float("inf")
glob_pct = total_rev / total_all * 100 if total_all > 0 else 0

print(f"""
Gesamtdatensatz:
  Revisit Cities:           {total_rev:.0f}
  New Cities:               {total_new:.0f}
  Ratio (revisit / new):    {glob_ratio:.3f}
  % Revisit (Städte):       {glob_pct:.1f}%
  Ø pct_revisit_cities:     {df_f4['pct_revisit_cities'].mean():.1f}%
  Median pct_revisit:       {df_f4['pct_revisit_cities'].median():.1f}%
  Ø pct_events_revisit:     {df_f4['pct_events_revisit'].mean():.1f}%
""")

# ══════════════════════════════════════════════════════════════════════════
# B) KORRELATIONSANALYSE
# ══════════════════════════════════════════════════════════════════════════
print(SEP)
print("B) KORRELATIONSANALYSE")
print(SEP)

tests = [
    ("pct_revisit_cities", "total_events", False),
    ("pct_revisit_cities", "listeners", True),
    ("revisit_ratio", "total_events", False),
    ("pct_events_revisit", "total_events", False),
]

for x_col, y_col, log_y in tests:
    if y_col not in df_f4.columns:
        continue
    tmp = df_f4[[x_col, y_col]].copy()
    tmp[y_col] = pd.to_numeric(tmp[y_col], errors="coerce")
    tmp = tmp.dropna()
    if len(tmp) < 5:
        continue
    y_vals = np.log10(tmp[y_col] + 1) if log_y else tmp[y_col]
    r, p = stats.pearsonr(tmp[x_col], y_vals)
    sig = "✅" if p < 0.05 else "⚠️"
    y_lbl = f"log({y_col})" if log_y else y_col
    print(f"  {x_col:25s} vs {y_lbl:20s}  r={r:+.3f}  p={p:.4f}  n={len(tmp)}  {sig}")

# ══════════════════════════════════════════════════════════════════════════
# C) GRUPPENVERGLEICH — Tour-Größe
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("C) GRUPPENVERGLEICH — pct_revisit_cities nach Tour-Größe (Quartile)")
print(SEP)

df_f4["tour_q"] = pd.qcut(
    df_f4["total_events"], q=4,
    labels=["Q1 Klein", "Q2 Mittel", "Q3 Groß", "Q4 Sehr groß"],
    duplicates="drop"
)
grp = df_f4.groupby("tour_q", observed=True)["pct_revisit_cities"].agg(
    ["mean", "median", "std", "count"]
).round(2)
print(grp.to_string())

kw_arrays = [
    df_f4[df_f4["tour_q"] == g]["pct_revisit_cities"].dropna().values
    for g in ["Q1 Klein", "Q2 Mittel", "Q3 Groß", "Q4 Sehr groß"]
    if len(df_f4[df_f4["tour_q"] == g]) > 1
]
if len(kw_arrays) >= 2:
    kw_stat, kw_p = stats.kruskal(*kw_arrays)
    print(f"\nKruskal-Wallis: H={kw_stat:.2f}  p={kw_p:.4f}  "
          f"→ {'Signifikant ✅' if kw_p < 0.05 else 'Nicht signifikant ⚠️'}")

# ══════════════════════════════════════════════════════════════════════════
# D) TOP / BOTTOM ARTISTS
# ══════════════════════════════════════════════════════════════════════════
cols_show = ["artist_name", "revisit_cities", "new_cities",
             "pct_revisit_cities", "revisit_ratio", "total_events"]

df_min5 = df_f4[df_f4["total_events"] >= 5]

print(f"\n{SEP}")
print("D) TOP 10 — Höchste Revisit-Rate (min. 5 Events)")
print(SEP)
print(df_min5.nlargest(10, "pct_revisit_cities")[cols_show].to_string(index=False))

print(f"\n{SEP}")
print("D) BOTTOM 10 — Niedrigste Revisit-Rate (min. 5 Events)")
print(SEP)
print(df_min5.nsmallest(10, "pct_revisit_cities")[cols_show].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# E) MEISTBESUCHTE STÄDTE
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("E) TOP 20 MEISTBESUCHTE STÄDTE (alle Artists)")
print(SEP)
top_cities = (
    city_df.groupby(["city", "country"])["visits"]
    .sum().sort_values(ascending=False).head(20).reset_index()
)
print(top_cities.to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# F) SPEICHERN
# ══════════════════════════════════════════════════════════════════════════
result_cols = [c for c in
               ["artist_name", "total_events", "revisit_cities", "new_cities",
                "pct_revisit_cities", "revisit_ratio", "pct_events_revisit",
                "most_visited_city", "most_visited_n", "listeners"]
               if c in df_f4.columns]

df_f4[result_cols].to_csv("data/processed/f4_results.csv", index=False)
print(f"\n✅  data/processed/f4_results.csv gespeichert")

# ══════════════════════════════════════════════════════════════════════════
# G) ANTWORT AUF FORSCHUNGSFRAGE
# ══════════════════════════════════════════════════════════════════════════
corr_tmp = df_f4.dropna(subset=["pct_revisit_cities", "total_events"])
r_fin, p_fin = stats.pearsonr(corr_tmp["pct_revisit_cities"], corr_tmp["total_events"])

print(f"\n{SEP}")
print("G) ANTWORT AUF FORSCHUNGSFRAGE F4")
print(SEP)
print(f"""
F4: What is the ratio of revisit cities to new cities on an artist's tour?

Globaler Ratio (revisit / new):   {glob_ratio:.3f}
→ Auf jede neue Stadt kommen {glob_ratio:.2f} Revisit-Städte

% Revisit Cities (Ø):             {df_f4['pct_revisit_cities'].mean():.1f}%
% Events in Revisit-Städten (Ø):  {df_f4['pct_events_revisit'].mean():.1f}%

Korrelation pct_revisit vs. Tour-Größe:
  r = {r_fin:.3f}  p = {p_fin:.4f}
  → {"Größere Tours revisiten anteilig mehr Städte." if r_fin > 0.1 and p_fin < 0.05
else "Größere Tours bereisen anteilig mehr neue Städte." if r_fin < -0.1 and p_fin < 0.05
else "Tour-Größe hat keinen wesentlichen Einfluss auf den Revisit-Anteil."}
""")
