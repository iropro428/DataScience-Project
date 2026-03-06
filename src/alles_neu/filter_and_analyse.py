# filter_and_analyse.py
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# Load
df_lastfm = pd.read_csv("data/artists_lastfm.csv")
df_events = pd.read_csv("data/ticketmaster_events.csv")

# Calculate Tour Size
tour_size = (
    df_events.groupby("artist_name")["event_id"]
    .count()
    .reset_index()
)
tour_size.columns = ["artist_name", "total_events"]

# Only Artists WITH Events
tour_size = tour_size[tour_size["total_events"] > 0]
print(f"Artists mit Events: {len(tour_size)}")

# Join
df = tour_size.merge(
    df_lastfm[["name", "listeners", "playcount"]],
    left_on="artist_name",
    right_on="name",
    how="inner"  # Only Artists that are present in BOTH datasets
)

print(f"Artists nach Join: {len(df)}")
print("\n=== Dataset ===")
print(df[["artist_name", "listeners", "total_events"]].to_string())

# Correlation 
r, p = stats.pearsonr(df["listeners"], df["total_events"])

print(f"\n=== Pearson Korrelation ===")
print(f"n  = {len(df)} Artists")
print(f"r  = {r:.3f}")
print(f"p  = {p:.4f}")
print(f"→  {'signifikant' if p < 0.05 else 'nicht signifikant (zu wenig Artists)'}")

# Plot
plt.figure(figsize=(12, 7))
plt.scatter(df["listeners"], df["total_events"],
            color="steelblue", s=100, zorder=5)

for _, row in df.iterrows():
    plt.annotate(row["artist_name"],
                 (row["listeners"], row["total_events"]),
                 textcoords="offset points",
                 xytext=(8, 4), fontsize=8)

# Trendline
m, b = stats.linregress(df["listeners"], df["total_events"])[:2]
x_line = [df["listeners"].min(), df["listeners"].max()]
y_line = [m * x + b for x in x_line]
plt.plot(x_line, y_line, color="red", linestyle="--", alpha=0.7, label="Trendlinie")

plt.xlabel("Last.fm Listeners", fontsize=12)
plt.ylabel("Anzahl Events (Ticketmaster)", fontsize=12)
plt.title(f"Last.fm Listeners vs Tour Scale\nr = {r:.3f} | p = {p:.4f} | n = {len(df)} Artists", fontsize=14)
plt.legend()
plt.tight_layout()
plt.savefig("data/correlation_plot.png", dpi=150)
plt.show()

print("\n Plot gespeichert → data/correlation_plot.png")
