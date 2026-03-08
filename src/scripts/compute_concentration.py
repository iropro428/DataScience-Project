# Berechnet Streaming-Konzentrations-Metriken aus lastfm_toptracks.csv
# Wird von join_data.py aufgerufen ODER standalone ausführbar
import pandas as pd
import numpy as np
import os

def compute_concentration(df_tracks: pd.DataFrame) -> pd.DataFrame:
    """
    Eingabe: DataFrame mit Spalten [artist_name, rank, playcount]
    Ausgabe: DataFrame mit Konzentrations-Metriken pro Artist

    Metriken:
      top1_share   — Anteil Track #1 am Gesamt-Playcount (%)
      top3_share   — Anteil Top-3 am Gesamt-Playcount (%)
      top5_share   — Anteil Top-5 am Gesamt-Playcount (%)  ← Haupt-Metrik F2
      hhi          — Herfindahl-Hirschman Index (0–10000), Maß für Konzentration
      n_tracks     — Anzahl Tracks mit Daten
      total_track_plays — Summe aller Track-Playcounts
    """
    results = []

    for artist, grp in df_tracks.groupby("artist_name"):
        grp = grp.sort_values("rank").reset_index(drop=True)
        grp["playcount"] = pd.to_numeric(grp["playcount"], errors="coerce").fillna(0)

        total = grp["playcount"].sum()
        if total == 0:
            continue

        shares = grp["playcount"] / total  # Anteil jedes Tracks

        top1  = grp[grp["rank"] <= 1]["playcount"].sum()
        top3  = grp[grp["rank"] <= 3]["playcount"].sum()
        top5  = grp[grp["rank"] <= 5]["playcount"].sum()

        # HHI = Summe der quadrierten Marktanteile × 10000
        # 0 = perfekte Gleichverteilung, 10000 = ein Track hat alles
        hhi = float((shares ** 2).sum() * 10000)

        results.append({
            "artist_name":       artist,
            "top1_share":        round(top1 / total * 100, 2),
            "top3_share":        round(top3 / total * 100, 2),
            "top5_share":        round(top5 / total * 100, 2),   # ← F2 x-Achse
            "hhi":               round(hhi, 1),
            "n_tracks":          len(grp),
            "total_track_plays": int(total),
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    path = "data/raw/lastfm_toptracks.csv"
    if not os.path.exists(path):
        print(f"❌ {path} nicht gefunden — erst collect_toptracks.py ausführen")
        exit(1)

    df_tracks = pd.read_csv(path)
    df_conc   = compute_concentration(df_tracks)

    os.makedirs("data/processed", exist_ok=True)
    df_conc.to_csv("data/processed/streaming_concentration.csv", index=False)

    print(f"✅ {len(df_conc)} Artists → data/processed/streaming_concentration.csv")
    print(f"\nBeispiel:")
    print(df_conc.head(10).to_string())
    print(f"\nStatistik top5_share:")
    print(df_conc["top5_share"].describe().round(2))
