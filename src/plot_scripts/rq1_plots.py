import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# -----------------------------
# CONFIG
# -----------------------------
DATA_PATH = "data/processed/final_dataset.csv"
PLOT_DIR = "data/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

SCATTER_PATH = os.path.join(PLOT_DIR, "f1_graph1_scatter_listeners_vs_events.png")
BAR_PATH = os.path.join(PLOT_DIR, "f1_graph2_events_per_listener_quartile.png")
HIST_PATH = os.path.join(PLOT_DIR, "f1_graph3_distribution_listeners.png")

# -----------------------------
# LOAD + CLEAN
# -----------------------------
df = pd.read_csv(DATA_PATH)

needed_cols = ["artist_name", "listeners", "total_events", "tags"]
missing = [c for c in needed_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns in final_dataset.csv: {missing}")

df = df[needed_cols].copy()

df["listeners"] = pd.to_numeric(df["listeners"], errors="coerce")
df["total_events"] = pd.to_numeric(df["total_events"], errors="coerce")

df = df.dropna(subset=["listeners", "total_events"]).copy()
df = df[df["listeners"] > 0]
df = df[df["total_events"] >= 0]

print(f"Artists after cleaning: {len(df)}")

# -----------------------------
# GLOBAL STATS
# -----------------------------
r, p = stats.pearsonr(df["listeners"], df["total_events"])
r2 = r ** 2
mean_listeners = df["listeners"].mean()
median_listeners = df["listeners"].median()
skewness = stats.skew(df["listeners"], nan_policy="omit")

print("\n=== Correlation Results ===")
print(f"n       = {len(df)}")
print(f"r       = {r:.4f}")
print(f"r²      = {r2:.4f}")
print(f"p       = {p:.4f}")
print(f"mean    = {mean_listeners:,.0f}")
print(f"median  = {median_listeners:,.0f}")
print(f"skew    = {skewness:.4f}")

# -----------------------------
# GRAPH 1: SCATTERPLOT
# -----------------------------
slope, intercept, _, _, std_err = stats.linregress(df["listeners"], df["total_events"])

x_line = np.linspace(df["listeners"].min(), df["listeners"].max(), 200)
y_line = slope * x_line + intercept

n = len(df)
x_mean = df["listeners"].mean()
ssx = np.sum((df["listeners"] - x_mean) ** 2)

# confidence band
se_line = std_err * np.sqrt(1 / n + (x_line - x_mean) ** 2 / ssx)
t_crit = stats.t.ppf(0.975, df=n - 2)
lower = y_line - t_crit * se_line
upper = y_line + t_crit * se_line

plt.figure(figsize=(14, 8))
plt.scatter(
    df["listeners"],
    df["total_events"],
    c=df["total_events"],
    cmap="viridis",
    s=65,
    alpha=0.75,
    edgecolors="white",
    linewidths=0.4
)

plt.plot(x_line, y_line, color="#00e676", linewidth=2.5, label="OLS")
plt.fill_between(x_line, lower, upper, color="#00e676", alpha=0.15)

plt.title(
    f"Last.fm Listeners vs. Tour-Scale | r = {r:.3f} | n = {len(df)} artists",
    fontsize=16,
    fontweight="bold"
)
plt.xlabel("Last.fm Listeners", fontsize=13)
plt.ylabel("Number of Scheduled Events", fontsize=13)
plt.grid(True, alpha=0.25)

plt.ticklabel_format(style="plain", axis="x")
plt.gca().xaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", "."))
)

# annotate top event artists
top_artists = df.nlargest(8, "total_events")
for _, row in top_artists.iterrows():
    plt.annotate(
        row["artist_name"],
        (row["listeners"], row["total_events"]),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=8,
        alpha=0.9
    )

plt.legend()
plt.tight_layout()
plt.savefig(SCATTER_PATH, dpi=220, bbox_inches="tight")
plt.close()

# -----------------------------
# GRAPH 2: BARPLOT (QUARTILES)
# -----------------------------
quartile_df = df.copy()

# qcut into 4 equally sized groups
quartile_df["listener_group"] = pd.qcut(
    quartile_df["listeners"],
    q=4,
    labels=["G1", "G2", "G3", "G4"]
)

quartile_summary = (
    quartile_df.groupby("listener_group", observed=False)["total_events"]
    .agg(["mean", "median", "count"])
    .reset_index()
)

quartile_summary["mean"] = quartile_summary["mean"].round(1)
quartile_summary["median"] = quartile_summary["median"].round(1)

print("\n=== Quartile Summary ===")
print(quartile_summary)

bar_values = quartile_summary["mean"]
groups = quartile_summary["listener_group"]

colors = ["#003b1f", "#1f9440", "#1fd063", "#10f08a"]

plt.figure(figsize=(12, 7))
bars = plt.bar(groups, bar_values, color=colors)

plt.title(
    "Average Number of Events per Listener Group (4 Groups, G1 = Lowest Listeners)",
    fontsize=15,
    fontweight="bold"
)
plt.xlabel("Listener Group", fontsize=12)
plt.ylabel("Average Events", fontsize=12)
plt.ylim(0, max(bar_values) * 1.25)
plt.grid(axis="y", alpha=0.25)

for bar, value in zip(bars, bar_values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.3,
        f"{value:.1f}",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )

plt.tight_layout()
plt.savefig(BAR_PATH, dpi=220, bbox_inches="tight")
plt.close()

# -----------------------------
# GRAPH 3: HISTOGRAM
# -----------------------------
plt.figure(figsize=(14, 8))
counts, bins, patches = plt.hist(
    df["listeners"],
    bins=18,
    color="#28a745",
    edgecolor="#1d6f32",
    alpha=0.95
)

plt.axvline(mean_listeners, color="#ffb000", linestyle="--", linewidth=2, label=f"Mean: {mean_listeners:,.0f}".replace(",", "."))
plt.axvline(median_listeners, color="#ff6b6b", linestyle=":", linewidth=2.2, label=f"Median: {median_listeners:,.0f}".replace(",", "."))

plt.title(
    "Distribution of Last.fm Listeners Across All Artists",
    fontsize=16,
    fontweight="bold"
)
plt.xlabel("Last.fm Listeners", fontsize=13)
plt.ylabel("Number of Artists", fontsize=13)
plt.grid(axis="y", alpha=0.25)

plt.ticklabel_format(style="plain", axis="x")
plt.gca().xaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", "."))
)

plt.legend()
plt.tight_layout()
plt.savefig(HIST_PATH, dpi=220, bbox_inches="tight")
plt.close()

# -----------------------------
# INTERPRETATION TEXT
# -----------------------------
if abs(r) >= 0.7:
    strength = "strong"
elif abs(r) >= 0.4:
    strength = "moderate"
else:
    strength = "weak"

direction = "positive" if r > 0 else "negative"

significance = "statistically significant" if p < 0.05 else "not statistically significant"

print("\n=== Interpretation ===")
print(
    f"The Pearson correlation between Last.fm listeners and the number of scheduled events "
    f"is r = {r:.3f}, indicating a {strength} {direction} relationship. "
    f"The result is {significance} (p = {p:.4f}). "
    f"The R² of {r2:.3f} means that listeners explain {r2 * 100:.1f}% of the variance in tour size."
)

print("\n=== Files saved ===")
print(SCATTER_PATH)
print(BAR_PATH)
print(HIST_PATH)