# analyse_f3.py
# Standalone Analyse für F3:
# Last.fm Listeners — Chart Artists vs. Non-Chart Artists (Spotify Weekly 2023–2026)
#
# Voraussetzung:
#   1. python scripts/process_spotify_charts.py
#   2. python scripts/join_data.py
#      (oder direkt: join_f3.py ausführen um was_on_chart zu ergänzen)
#
# Output Console + data/processed/f3_results.csv

import pandas as pd
import numpy as np
from scipy import stats
import os, sys

FINAL  = "data/processed/final_dataset.csv"
CHARTS = "data/processed/spotify_charts/chart_artists.csv"

for p in [FINAL, CHARTS]:
    if not os.path.exists(p):
        print(f"❌  {p} fehlt")
        if p == CHARTS:
            print("   → python scripts/process_spotify_charts.py ausführen")
        sys.exit(1)

df     = pd.read_csv(FINAL)
charts = pd.read_csv(CHARTS)

# ── Join: was_on_chart Flag ───────────────────────────────────────────────
# Normalisierter Artist-Name-Vergleich (lowercase, stripped)
charts["artist_norm"] = charts["artist"].str.lower().str.strip()
df["artist_norm"]     = df["artist_name"].str.lower().str.strip()

chart_set    = set(charts["artist_norm"])
df["was_on_chart"] = df["artist_norm"].isin(chart_set)

# Optionale Chart-Metriken joinen
chart_cols = ["artist_norm","total_chart_streams","chart_weeks","peak_position",
              "first_chart_date","last_chart_date"]
chart_cols = [c for c in chart_cols if c in charts.columns]
df = df.merge(charts[chart_cols], on="artist_norm", how="left")
df.drop(columns=["artist_norm"], inplace=True)

for c in ["listeners","playcount","total_events","events_last_year"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

SEP = "=" * 60
n_chart     = df["was_on_chart"].sum()
n_non_chart = (~df["was_on_chart"]).sum()
n_total     = len(df)

print(f"\n{SEP}")
print(f"F3 ANALYSE: Chart Artists vs. Non-Chart Artists")
print(f"{SEP}")
print(f"Artists gesamt:          {n_total}")
print(f"Im Spotify Chart:        {n_chart}  ({n_chart/n_total*100:.0f}%)")
print(f"Nicht im Chart:          {n_non_chart}  ({n_non_chart/n_total*100:.0f}%)")

# ══════════════════════════════════════════════════════════════════════════
# A) DESKRIPTIVE STATISTIK
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("A) DESKRIPTIVE STATISTIK — Last.fm Listeners")
print(SEP)

for label, mask in [("Chart Artists", df["was_on_chart"]),
                    ("Non-Chart Artists", ~df["was_on_chart"])]:
    sub = df[mask]["listeners"].dropna()
    if len(sub) == 0: continue
    print(f"\n  {label} (n={len(sub)}):")
    print(f"    Mittelwert:   {sub.mean():>15,.0f}")
    print(f"    Median:       {sub.median():>15,.0f}")
    print(f"    Std:          {sub.std():>15,.0f}")
    print(f"    Min:          {sub.min():>15,.0f}")
    print(f"    Max:          {sub.max():>15,.0f}")
    print(f"    Q25:          {sub.quantile(.25):>15,.0f}")
    print(f"    Q75:          {sub.quantile(.75):>15,.0f}")

# Verhältnis
mean_c  = df[df["was_on_chart"]]["listeners"].mean()
mean_nc = df[~df["was_on_chart"]]["listeners"].mean()
if mean_nc and mean_nc > 0:
    print(f"\n  → Chart Artists haben Ø {mean_c/mean_nc:.1f}× mehr Listeners als Non-Chart Artists")

# ══════════════════════════════════════════════════════════════════════════
# B) STATISTISCHE TESTS
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("B) STATISTISCHE TESTS")
print(SEP)

grp_c  = df[df["was_on_chart"]]["listeners"].dropna()
grp_nc = df[~df["was_on_chart"]]["listeners"].dropna()

if len(grp_c) >= 5 and len(grp_nc) >= 5:

    # Mann-Whitney U (nicht-parametrisch, robust bei schiefer Verteilung)
    u_stat, u_p = stats.mannwhitneyu(grp_c, grp_nc, alternative="two-sided")
    print(f"\n  Mann-Whitney U:")
    print(f"    U = {u_stat:.1f}  p = {u_p:.6f}  → {'Signifikant ✅' if u_p < 0.05 else 'Nicht signifikant ⚠️'}")
    print(f"    (Nicht-parametrisch, robust gegenüber Ausreißern)")

    # t-Test auf log-transformierten Daten
    log_c  = np.log10(grp_c  + 1)
    log_nc = np.log10(grp_nc + 1)
    t_stat, t_p = stats.ttest_ind(log_c, log_nc, equal_var=False)  # Welch's t-test
    print(f"\n  Welch's t-Test (log10 Listeners):")
    print(f"    t = {t_stat:.3f}  p = {t_p:.6f}  → {'Signifikant ✅' if t_p < 0.05 else 'Nicht signifikant ⚠️'}")

    # Effect Size: Cohen's d auf log-Daten
    pooled_std = np.sqrt((log_c.std()**2 + log_nc.std()**2) / 2)
    cohens_d   = (log_c.mean() - log_nc.mean()) / pooled_std if pooled_std > 0 else 0
    effect_lbl = ("groß" if abs(cohens_d) >= 0.8 else
                  "mittel" if abs(cohens_d) >= 0.5 else
                  "klein"  if abs(cohens_d) >= 0.2 else "vernachlässigbar")
    print(f"\n  Effect Size Cohen's d (log): {cohens_d:.3f} → {effect_lbl}e Effektstärke")

    # Shapiro-Wilk Normalitätstest (Stichprobe ≤ 50)
    if len(grp_c) <= 50:
        sw_c, sw_p_c = stats.shapiro(grp_c)
        print(f"\n  Shapiro-Wilk (Chart, n={len(grp_c)}): W={sw_c:.3f}  p={sw_p_c:.4f}"
              f"  → {'Normal ✅' if sw_p_c > 0.05 else 'Nicht normal ❌ → Mann-Whitney bevorzugen'}")

# ══════════════════════════════════════════════════════════════════════════
# C) KORRELATION Chart-Intensität vs. Listeners
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("C) KORRELATION — Chart-Intensität vs. Last.fm Listeners")
print(SEP)

for col, label in [
    ("total_chart_streams", "Gesamt-Chart-Streams"),
    ("chart_weeks",         "Wochen im Chart"),
    ("peak_position",       "Peak Position (invers)"),
]:
    if col not in df.columns: continue
    tmp = df[df["was_on_chart"]].dropna(subset=[col, "listeners"])
    if len(tmp) < 5: continue
    x = tmp[col] if col != "peak_position" else -tmp[col]  # Position invertieren: niedriger = besser
    r, p = stats.pearsonr(np.log10(x.abs() + 1), np.log10(tmp["listeners"] + 1))
    print(f"  {label:<30} r = {r:+.3f}  p = {p:.4f}  {'✅' if p < 0.05 else '⚠️'}")

# ══════════════════════════════════════════════════════════════════════════
# D) GRUPPEN-BREAKDOWN — Chart-Intensität
# ══════════════════════════════════════════════════════════════════════════
if "chart_weeks" in df.columns:
    print(f"\n{SEP}")
    print("D) GRUPPEN — Last.fm Listeners nach Chart-Intensität")
    print(SEP)

    df_c = df[df["was_on_chart"]].copy()
    df_c["chart_weeks"] = pd.to_numeric(df_c["chart_weeks"], errors="coerce")
    df_c = df_c.dropna(subset=["chart_weeks"])

    if len(df_c) >= 4:
        try:
            bins   = [0, 4, 12, 26, float("inf")]
            labels = ["1–4 Wochen", "5–12 Wochen", "13–26 Wochen", ">26 Wochen"]
            df_c["intensity"] = pd.cut(df_c["chart_weeks"], bins=bins, labels=labels)
            grp = df_c.groupby("intensity", observed=True)["listeners"].agg(
                ["mean","median","count"]).round(0)
            print(grp.to_string())

            kw_arr = [df_c[df_c["intensity"]==g]["listeners"].dropna().values
                      for g in labels if len(df_c[df_c["intensity"]==g]) > 1]
            if len(kw_arr) >= 2:
                kw_h, kw_p = stats.kruskal(*kw_arr)
                print(f"\n  Kruskal-Wallis: H = {kw_h:.2f}  p = {kw_p:.4f}  "
                      f"→ {'Signifikant ✅' if kw_p < 0.05 else 'Nicht signifikant ⚠️'}")
        except Exception as e:
            print(f"  Fehler: {e}")

# ══════════════════════════════════════════════════════════════════════════
# E) TOP / BOTTOM
# ══════════════════════════════════════════════════════════════════════════
show_cols = [c for c in ["artist_name","was_on_chart","listeners","chart_weeks",
                          "total_chart_streams","peak_position","total_events"]
             if c in df.columns]

print(f"\n{SEP}")
print("E1) TOP 10 Chart-Artists nach Last.fm Listeners")
print(SEP)
print(df[df["was_on_chart"]].nlargest(10, "listeners")[show_cols].to_string(index=False))

print(f"\n{SEP}")
print("E2) TOP 10 Non-Chart-Artists nach Last.fm Listeners")
print(SEP)
print(df[~df["was_on_chart"]].nlargest(10, "listeners")[show_cols].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# F) SPEICHERN
# ══════════════════════════════════════════════════════════════════════════
save_cols = [c for c in ["artist_name","was_on_chart","listeners","playcount",
                          "total_events","events_last_year","total_chart_streams",
                          "chart_weeks","peak_position","first_chart_date","last_chart_date"]
             if c in df.columns]
df[save_cols].to_csv("data/processed/f3_results.csv", index=False)
print(f"\n✅  data/processed/f3_results.csv gespeichert")

# ══════════════════════════════════════════════════════════════════════════
# G) ANTWORT AUF FORSCHUNGSFRAGE
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("G) ANTWORT AUF FORSCHUNGSFRAGE F3")
print(SEP)

sig = u_p < 0.05 if 'u_p' in dir() else False
print(f"""
F3: How do current Last.fm listener counts differ between artists who appeared
    in Spotify Weekly Charts (Feb 2023 – Feb 2026) and those who did not?

Chart Artists:     {n_chart}  Ø {mean_c:,.0f} Listeners
Non-Chart Artists: {n_non_chart}  Ø {mean_nc:,.0f} Listeners
Verhältnis:        {mean_c/mean_nc:.1f}× höher bei Chart Artists

Mann-Whitney U:    p = {f'{u_p:.6f}' if 'u_p' in dir() else 'n/a'}  → {'Signifikant ✅' if sig else 'Nicht signifikant ⚠️'}
Cohen's d (log):   {f'{cohens_d:.3f}' if 'cohens_d' in dir() else 'n/a'}  → {effect_lbl if 'effect_lbl' in dir() else ''}

→ {"Chart-Auftritte gehen mit signifikant höheren Last.fm Listener-Zahlen einher — cross-platform Popularität ist konsistent." if sig
   else "Kein signifikanter Unterschied — Last.fm Listeners und Spotify Chart-Präsenz sind nicht stark korreliert in diesem Datensatz."}
""")
