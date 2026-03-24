import pandas as pd
import numpy as np
import os

def compute_concentration(df_tracks: pd.DataFrame) -> pd.DataFrame:
    # Input: DataFrame with columns [artist_name, rank, playcount]
    # Output: DataFrame with concentration metrics per artist
    # Metrics:
    #   top1_share — share of track #1 in the total playcount (%)
    #   top3_share — share of the top 3 tracks in the total playcount (%)
    #   top5_share — share of the top 5 tracks in the total playcount (%)  ← main metric F2
    #   hhi        — Herfindahl–Hirschman Index (0–10000), a measure of concentration
    #   n_tracks   — number of tracks with available data
    #   total_track_plays — total sum of all track playcounts
    
    results = []

    for artist, grp in df_tracks.groupby("artist_name"):
        grp = grp.sort_values("rank").reset_index(drop=True)
        grp["playcount"] = pd.to_numeric(grp["playcount"], errors="coerce").fillna(0)

        total = grp["playcount"].sum()
        if total == 0:
            continue

        shares = grp["playcount"] / total  # Proportion of each track

        top1  = grp[grp["rank"] <= 1]["playcount"].sum()
        top3  = grp[grp["rank"] <= 3]["playcount"].sum()
        top5  = grp[grp["rank"] <= 5]["playcount"].sum()

        # HHI = sum of squared market shares × 10000
        # 0 = perfectly equal distribution, 10000 = one track accounts for everything
        hhi = float((shares ** 2).sum() * 10000)

        results.append({
            "artist_name":       artist,
            "top1_share":        round(top1 / total * 100, 2),
            "top3_share":        round(top3 / total * 100, 2),
            "top5_share":        round(top5 / total * 100, 2),   # ← F2 x-axis
            "hhi":               round(hhi, 1),
            "n_tracks":          len(grp),
            "total_track_plays": int(total),
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    path = "data/raw/lastfm_toptracks.csv"
    if not os.path.exists(path):
        print(f"{path} not found — please run collect_toptracks.py first")
        exit(1)

    df_tracks = pd.read_csv(path)
    df_conc   = compute_concentration(df_tracks)

    os.makedirs("data/processed", exist_ok=True)
    df_conc.to_csv("data/processed/streaming_concentration.csv", index=False)

    print(f"{len(df_conc)} artists → data/processed/streaming_concentration.csv")
    print(f"\nExample:")
    print(df_conc.head(10).to_string())
    print(f"\nStatistics for top5_share:")
    print(df_conc["top5_share"].describe().round(2))
