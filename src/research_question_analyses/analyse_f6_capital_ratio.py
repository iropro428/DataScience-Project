# analyse_f6_capital_ratio.py
# Standalone Data-Science Analyse für F6: Capital vs. Non-Capital Cities
# Kein Streamlit — Console-Output + CSV
#
# Voraussetzung: join_data.py wurde ausgeführt
#
# Output:
#   Console — Statistik, Korrelationen, Rankings
#   data/processed/f6_results.csv

import pandas as pd
import numpy as np
from scipy import stats
import os, sys

for p in ["data/processed/final_dataset.csv",
          "data/processed/f6_capitals_visited.csv",
          "data/processed/f6_capitals_per_artist.csv"]:
    if not os.path.exists(p):
        print(f"❌  {p} fehlt — erst join_data.py ausführen")
        sys.exit(1)

df = pd.read_csv("data/processed/final_dataset.csv")
cap_gl = pd.read_csv("data/processed/f6_capitals_visited.csv")
cap_ar = pd.read_csv("data/processed/f6_capitals_per_artist.csv")

F6_COLS = ["capital_events", "non_capital_events", "pct_capital",
           "capital_ratio", "unique_capitals", "unique_non_capitals", "pct_capital_cities"]
missing = [c for c in F6_COLS if c not in df.columns]
if missing:
    print(f"❌  Fehlende Spalten: {missing} — join_data.py erneut ausführen")
    sys.exit(1)

for c in F6_COLS + ["total_events", "listeners"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

df_f6 = df.dropna(subset=["capital_events", "non_capital_events"]).copy()
SEP = "=" * 56

# ══════════════════════════════════════════════════════════════════════════
# A) DESKRIPTIVE STATISTIK
# ══════════════════════════════════════════════════════════════════════════
print(SEP)
print("A) DESKRIPTIVE STATISTIK")
print(SEP)
print(df_f6[F6_COLS].describe().round(2).to_string())

total_cap = df_f6["capital_events"].sum()
total_non = df_f6["non_capital_events"].sum()
total_all = total_cap + total_non
glob_pct = total_cap / total_all * 100 if total_all > 0 else 0
glob_ratio = total_cap / total_non if total_non > 0 else float("inf")

print(f"""
Gesamtdatensatz:
  Capital Events:           {total_cap:.0f}
  Non-Capital Events:       {total_non:.0f}
  % Capital Events:         {glob_pct:.1f}%
  Ratio (cap / non-cap):    {glob_ratio:.3f}

  Ø pct_capital:            {df_f6['pct_capital'].mean():.1f}%
  Median pct_capital:       {df_f6['pct_capital'].median():.1f}%
  Ø unique_capitals:        {df_f6['unique_capitals'].mean():.1f}
  Ø pct_capital_cities:     {df_f6['pct_capital_cities'].mean():.1f}%

  Artists mit 0% Capital:   {(df_f6['pct_capital'] == 0).sum()}
  Artists mit ≥50% Capital: {(df_f6['pct_capital'] >= 50).sum()}
  Artists mit 100% Capital: {(df_f6['pct_capital'] == 100).sum()}
""")

# ══════════════════════════════════════════════════════════════════════════
# B) KORRELATIONSANALYSE
# ══════════════════════════════════════════════════════════════════════════
print(SEP)
print("B) KORRELATIONSANALYSE")
print(SEP)

tests = [
    ("pct_capital", "total_events", False, "pct_capital vs Tour-Größe"),
    ("pct_capital", "listeners", True, "pct_capital vs log(listeners)"),
    ("unique_capitals", "total_events", False, "unique_capitals vs Tour-Größe"),
    ("pct_capital_cities", "total_events", False, "pct_capital_cities vs Tour-Größe"),
]
for x_col, y_col, log_y, label in tests:
    if y_col not in df_f6.columns:
        continue
    tmp = df_f6[[x_col, y_col]].dropna().copy()
    tmp[y_col] = pd.to_numeric(tmp[y_col], errors="coerce").dropna()
    tmp = tmp.dropna()
    if len(tmp) < 5:
        continue
    y_v = np.log10(tmp[y_col] + 1) if log_y else tmp[y_col]
    r, p = stats.pearsonr(tmp[x_col], y_v)
    print(f"  {label:<45} r={r:+.3f}  p={p:.4f}  n={len(tmp)}  "
          f"{'✅' if p < 0.05 else '⚠️'}")

# ══════════════════════════════════════════════════════════════════════════
# C) GRUPPENVERGLEICH — pct_capital nach Listeners-Quartil
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("C) pct_capital nach Listeners-Quartil")
print(SEP)

df_lq = df_f6.dropna(subset=["listeners", "pct_capital"]).copy()
df_lq["listeners_q"] = pd.qcut(df_lq["listeners"], q=4,
                               labels=["Q1 niedrig", "Q2", "Q3", "Q4 hoch"], duplicates="drop")
grp = df_lq.groupby("listeners_q", observed=True)["pct_capital"].agg(
    ["mean", "median", "count"]).round(2)
print(grp.to_string())

kw_arr = [df_lq[df_lq["listeners_q"] == g]["pct_capital"].dropna().values
          for g in ["Q1 niedrig", "Q2", "Q3", "Q4 hoch"]
          if len(df_lq[df_lq["listeners_q"] == g]) > 1]
if len(kw_arr) >= 2:
    kw_h, kw_p = stats.kruskal(*kw_arr)
    print(f"\nKruskal-Wallis: H={kw_h:.2f}  p={kw_p:.4f}  "
          f"→ {'Signifikant ✅' if kw_p < 0.05 else 'Nicht signifikant ⚠️'}")

# ══════════════════════════════════════════════════════════════════════════
# D) TOP / BOTTOM ARTISTS
# ══════════════════════════════════════════════════════════════════════════
cols_show = ["artist_name", "capital_events", "non_capital_events", "pct_capital",
             "unique_capitals", "total_events"]
df_min5 = df_f6[df_f6["total_events"] >= 5]

print(f"\n{SEP}")
print("D) TOP 10 — Höchster Capital-Anteil (min. 5 Events)")
print(SEP)
print(df_min5.nlargest(10, "pct_capital")[cols_show].to_string(index=False))

print(f"\n{SEP}")
print("D) BOTTOM 10 — Niedrigster Capital-Anteil (min. 5 Events)")
print(SEP)
print(df_min5.nsmallest(10, "pct_capital")[cols_show].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# E) MEISTBESUCHTE HAUPTSTÄDTE
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("E) TOP 20 MEISTBESUCHTE HAUPTSTÄDTE (alle Artists)")
print(SEP)
print(cap_gl.head(20).to_string(index=False))

# Artists pro Hauptstadt
print(f"\n{SEP}")
print("E2) TOP 10 — Hauptstädte nach Anzahl verschiedener Artists")
print(SEP)
print(cap_gl.nlargest(10, "n_artists")[["city", "country", "n_artists", "total_visits"]].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# F) SPEICHERN
# ══════════════════════════════════════════════════════════════════════════
result_cols = [c for c in
               ["artist_name", "total_events", "capital_events", "non_capital_events",
                "pct_capital", "capital_ratio", "unique_capitals", "unique_non_capitals",
                "pct_capital_cities", "listeners"]
               if c in df_f6.columns]
df_f6[result_cols].to_csv("data/processed/f6_results.csv", index=False)
print(f"\n✅  data/processed/f6_results.csv gespeichert")

# ══════════════════════════════════════════════════════════════════════════
# G) ANTWORT AUF FORSCHUNGSFRAGE
# ══════════════════════════════════════════════════════════════════════════
corr_tmp = df_f6.dropna(subset=["pct_capital", "total_events"])
r_g, p_g = stats.pearsonr(corr_tmp["pct_capital"], corr_tmp["total_events"])

print(f"\n{SEP}")
print("G) ANTWORT AUF FORSCHUNGSFRAGE F6")
print(SEP)
print(f"""
F6: What proportion of an artist's performances take place in capital cities?

Globaler Anteil Capital-Events:    {glob_pct:.1f}%
Ratio (Capital / Non-Capital):     {glob_ratio:.3f}
Ø pct_capital pro Artist:          {df_f6['pct_capital'].mean():.1f}%
Ø pct_capital_cities:              {df_f6['pct_capital_cities'].mean():.1f}%
Ø Hauptstädte besucht / Artist:    {df_f6['unique_capitals'].mean():.1f}

Korrelation pct_capital vs Tour-Größe:
  r = {r_g:.3f}  p = {p_g:.4f}
  → {"Populärere Artists spielen anteilig mehr in Hauptstädten." if r_g > 0.1 and p_g < 0.05
else "Populärere Artists spielen anteilig weniger in Hauptstädten — breitere geografische Streuung." if r_g < -0.1 and p_g < 0.05
else "Kein signifikanter Zusammenhang zwischen Tour-Größe und Capital-Anteil."}
""")
