# Standalone Data-Science Analyse für F2:
# Streaming-Konzentration (Top-Track-Anteil) vs. Tour-Intensität (Events/Jahr)
#
# Voraussetzung: join_data.py wurde ausgeführt (benötigt lastfm_toptracks.csv)
#
# Output Console:
#   A) Deskriptive Statistik (Konzentrationsmetriken)
#   B) Korrelationsanalyse (alle 4 Metriken vs. Events/Jahr)
#   C) Gruppenvergleich — Tour-Intensität nach Konzentrations-Kategorie
#   D) Top/Bottom Artists
#   E) Track-Profil: extremste Fälle
#   F) Antwort auf Forschungsfrage
#
# Output Dateien:
#   data/processed/f2_results.csv

import pandas as pd
import numpy as np
from scipy import stats
import os, sys

# ── Laden ──────────────────────────────────────────────────────────────────
FINAL = "data/processed/final_dataset.csv"
TRACKS = "data/raw/lastfm_toptracks.csv"

if not os.path.exists(FINAL):
    print(f"❌  {FINAL} fehlt — erst join_data.py ausführen")
    sys.exit(1)

df = pd.read_csv(FINAL)

F2_COLS = ["top5_share", "events_last_year"]
missing = [c for c in F2_COLS if c not in df.columns]
if missing:
    print(f"❌  Fehlende Spalten: {missing}")
    print("   → collect_toptracks.py + join_data.py ausführen")
    sys.exit(1)

for c in ["top5_share", "top3_share", "top1_share", "hhi",
          "events_last_year", "total_events", "listeners", "n_tracks", "total_track_plays"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

df_f2 = df.dropna(subset=["top5_share", "events_last_year"]).copy()

# Coverage
total_artists = len(df)
f2_artists = len(df_f2)
coverage_pct = f2_artists / total_artists * 100

SEP = "=" * 60
print(f"\n{SEP}")
print(f"F2 ANALYSE: Streaming-Konzentration vs. Tour-Intensität")
print(f"{SEP}")
print(f"Artists gesamt:         {total_artists}")
print(f"Artists mit F2-Daten:   {f2_artists}  ({coverage_pct:.0f}%)")
print(f"Artists ohne Toptracks: {total_artists - f2_artists}")

# ══════════════════════════════════════════════════════════════════════════
# A) DESKRIPTIVE STATISTIK
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("A) DESKRIPTIVE STATISTIK — Konzentrations-Metriken")
print(SEP)

conc_cols = [c for c in ["top1_share", "top3_share", "top5_share", "hhi",
                         "n_tracks", "events_last_year", "total_events"]
             if c in df_f2.columns]
print(df_f2[conc_cols].describe().round(2).to_string())

print(f"""
Konzentrations-Verteilung (top5_share):
  Ø top5_share:    {df_f2['top5_share'].mean():.1f}%
  Median:          {df_f2['top5_share'].median():.1f}%
  Std:             {df_f2['top5_share'].std():.1f}%
  Min → Max:       {df_f2['top5_share'].min():.1f}% → {df_f2['top5_share'].max():.1f}%

  < 40%  (breites Profil):          {(df_f2['top5_share'] < 40).sum()} Artists  ({(df_f2['top5_share'] < 40).mean() * 100:.0f}%)
  40–60% (moderates Profil):        {((df_f2['top5_share'] >= 40) & (df_f2['top5_share'] < 60)).sum()} Artists
  ≥ 60%  (konzentriertes Profil):   {(df_f2['top5_share'] >= 60).sum()} Artists  ({(df_f2['top5_share'] >= 60).mean() * 100:.0f}%)

Tour-Intensität (events_last_year):
  Ø Events/Jahr:   {df_f2['events_last_year'].mean():.1f}
  Median:          {df_f2['events_last_year'].median():.1f}
  Artists mit 0 Events/Jahr: {(df_f2['events_last_year'] == 0).sum()}
""")

# ══════════════════════════════════════════════════════════════════════════
# B) KORRELATIONSANALYSE — alle Metriken
# ══════════════════════════════════════════════════════════════════════════
print(f"{SEP}")
print("B) KORRELATIONSANALYSE — Konzentration vs. Tour-Intensität")
print(SEP)

metrics = [
    ("top5_share", "Top-5 Anteil (%)"),
    ("top3_share", "Top-3 Anteil (%)"),
    ("top1_share", "Top-1 Anteil (%)"),
    ("hhi", "HHI (0–10000)"),
]
y_variants = [
    ("events_last_year", "Events/Jahr", False),
    ("events_last_year", "log(Events/Jahr)", True),
    ("total_events", "Events gesamt", False),
]

print(f"\n{'Metrik':<25} {'Y-Variable':<25} {'r':>7} {'R²':>6} {'p':>8} {'sig':>4}")
print("-" * 75)
for x_col, x_lbl in metrics:
    if x_col not in df_f2.columns:
        continue
    for y_col, y_lbl, log_y in y_variants:
        if y_col not in df_f2.columns:
            continue
        tmp = df_f2[[x_col, y_col]].dropna()
        if len(tmp) < 5:
            continue
        y_v = np.log10(tmp[y_col] + 1) if log_y else tmp[y_col]
        r, p = stats.pearsonr(tmp[x_col], y_v)
        r2 = r ** 2
        sig = "✅" if p < 0.05 else "⚠️"
        print(f"  {x_lbl:<23} {y_lbl:<25} {r:>+7.3f} {r2:>6.1%} {p:>8.4f} {sig}")

# Spearman für Robustheit
print(f"\n--- Spearman ρ (robuster gegenüber Ausreißern) ---")
for x_col, x_lbl in metrics[:2]:
    if x_col not in df_f2.columns:
        continue
    tmp = df_f2[[x_col, "events_last_year"]].dropna()
    rho, p_sp = stats.spearmanr(tmp[x_col], tmp["events_last_year"])
    print(f"  {x_lbl:<25} vs Events/Jahr  ρ = {rho:+.3f}  p = {p_sp:.4f}  "
          f"{'✅' if p_sp < 0.05 else '⚠️'}")

# ══════════════════════════════════════════════════════════════════════════
# C) GRUPPENVERGLEICH — Kruskal-Wallis
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("C) GRUPPENVERGLEICH — Events/Jahr nach Konzentrations-Kategorie")
print(SEP)

n_cats_list = [3, 4, 5]
for n_cats in n_cats_list:
    try:
        labels = {
            3: ["Breit (0–33%)", "Mittel (33–67%)", "Konzentriert (67–100%)"],
            4: ["Breit", "Moderat", "Konzentriert", "Sehr konzentriert"],
            5: ["Sehr breit", "Breit", "Moderat", "Konzentriert", "Sehr konzentriert"],
        }[n_cats]
        df_f2["cat_tmp"] = pd.qcut(df_f2["top5_share"], q=n_cats,
                                   labels=labels, duplicates="drop")
        grp = df_f2.groupby("cat_tmp", observed=True)["events_last_year"].agg(
            ["mean", "median", "std", "count"]).round(2)
        print(f"\n{n_cats} Gruppen (Quartile von top5_share):")
        print(grp.to_string())

        kw_arr = [df_f2[df_f2["cat_tmp"] == g]["events_last_year"].dropna().values
                  for g in labels if len(df_f2[df_f2["cat_tmp"] == g]) > 1]
        if len(kw_arr) >= 2:
            h, p = stats.kruskal(*kw_arr)
            print(f"  Kruskal-Wallis: H = {h:.2f}  p = {p:.4f}  "
                  f"→ {'Signifikant ✅' if p < 0.05 else 'Nicht signifikant ⚠️'}")
    except Exception as e:
        print(f"  Fehler bei {n_cats} Gruppen: {e}")

df_f2.drop(columns=["cat_tmp"], errors="ignore", inplace=True)

# ══════════════════════════════════════════════════════════════════════════
# D) TOP / BOTTOM ARTISTS
# ══════════════════════════════════════════════════════════════════════════
cols_show = [c for c in ["artist_name", "top5_share", "top1_share", "hhi",
                         "events_last_year", "total_events", "listeners"]
             if c in df_f2.columns]
df_min3 = df_f2[df_f2["events_last_year"] >= 1]

print(f"\n{SEP}")
print("D1) TOP 10 — Höchste Streaming-Konzentration (min. 1 Event/Jahr)")
print(SEP)
print(df_min3.nlargest(10, "top5_share")[cols_show].to_string(index=False))

print(f"\n{SEP}")
print("D2) BOTTOM 10 — Niedrigste Streaming-Konzentration (min. 1 Event/Jahr)")
print(SEP)
print(df_min3.nsmallest(10, "top5_share")[cols_show].to_string(index=False))

print(f"\n{SEP}")
print("D3) TOP 10 — Tour-Intensivste Artists (Events/Jahr)")
print(SEP)
print(df_f2.nlargest(10, "events_last_year")[cols_show].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# E) TRACK-PROFIL: Extremfälle (wenn Toptracks vorhanden)
# ══════════════════════════════════════════════════════════════════════════
if os.path.exists(TRACKS):
    print(f"\n{SEP}")
    print("E) TRACK-PROFIL — Top-3 konzentrierteste und breiteste Artists")
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
        tag = "🔴 konzentriert" if top5 >= 60 else "🟡 moderat" if top5 >= 40 else "🟢 breit"

        print(f"\n  {artist}  [{tag}]")
        print(f"    top5_share = {top5:.1f}%  |  Events/Jahr = {ev:.0f}")

        if len(tracks) > 0:
            total_pc = df_tracks[df_tracks["artist_name"] == artist]["playcount"].sum()
            for _, t in tracks.iterrows():
                pct = t["playcount"] / total_pc * 100 if total_pc > 0 else 0
                bar = "█" * int(pct / 4)
                print(f"    #{int(t['rank']):<2} {str(t['track_name'])[:30]:<30} {pct:>5.1f}%  {bar}")

# ══════════════════════════════════════════════════════════════════════════
# F) ERGEBNIS SPEICHERN
# ══════════════════════════════════════════════════════════════════════════
result_cols = [c for c in
               ["artist_name", "top5_share", "top3_share", "top1_share", "hhi",
                "n_tracks", "total_track_plays", "events_last_year", "total_events", "listeners"]
               if c in df_f2.columns]

df_f2[result_cols].to_csv("data/processed/f2_results.csv", index=False)
print(f"\n\n✅  data/processed/f2_results.csv gespeichert")

# ══════════════════════════════════════════════════════════════════════════
# G) ANTWORT AUF FORSCHUNGSFRAGE
# ══════════════════════════════════════════════════════════════════════════
tmp_main = df_f2[["top5_share", "events_last_year"]].dropna()
r_ans, p_ans = stats.pearsonr(tmp_main["top5_share"], tmp_main["events_last_year"])
r2_ans = r_ans ** 2
sig_ans = p_ans < 0.05

print(f"\n{SEP}")
print("G) ANTWORT AUF FORSCHUNGSFRAGE F2")
print(SEP)
print(f"""
F2: How does the concentration of an artist's streaming activity on a few
    top tracks relate to the intensity of their touring?

Dataset:        {f2_artists} Artists  ({coverage_pct:.0f}% Coverage)
Metrik X:       top5_share — Anteil Top-5 Tracks am Gesamt-Playcount
Metrik Y:       events_last_year — Konzerte in den letzten 12 Monaten

Pearson r:      {r_ans:+.3f}
R²:             {r2_ans:.1%}
p-Wert:         {p_ans:.4f}
Signifikant:    {'Ja ✅' if sig_ans else 'Nein ⚠️'}

Ø top5_share:        {df_f2['top5_share'].mean():.1f}%
Ø events_last_year:  {df_f2['events_last_year'].mean():.1f}

→ {"Die Hypothese wird BESTÄTIGT: Niedrige Streaming-Konzentration (breites Katalog-Publikum) korreliert mit höherer Tour-Intensität." if r_ans < -0.2 and sig_ans
else "Die Hypothese wird WIDERLEGT: Hohe Streaming-Konzentration (wenige Hit-Tracks) korreliert mit höherer Tour-Intensität." if r_ans > 0.2 and sig_ans
else "Kein signifikanter Zusammenhang: Die Struktur der Streaming-Aktivität (breit vs. konzentriert) hat keinen wesentlichen Einfluss auf die Tour-Intensität."}
""")
