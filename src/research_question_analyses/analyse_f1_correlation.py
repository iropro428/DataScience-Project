# Analyse_f1_correlation.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats
import numpy as np
import os

# Load
df = pd.read_csv("data/processed/final_dataset.csv")
os.makedirs("data/plots", exist_ok=True)

print(f"Geladene Artists: {len(df)}")
print(f"Fehlende Werte:\n{df[['listeners', 'total_events']].isnull().sum()}")

# Clean
df = df.dropna(subset=["listeners", "total_events"])
df = df[df["total_events"] > 0]
print(f"\nNach Bereinigung: {len(df)} Artists")

# Descriptive statistics
print("\n=== Deskriptive Statistik ===")
print(df[["listeners", "total_events"]].describe().round(2))

# Pearson correlation
r, p = stats.pearsonr(df["listeners"], df["total_events"])

# Determine strenght
if abs(r) >= 0.7:
    strength = "stark"
elif abs(r) >= 0.4:
    strength = "moderat"
else:
    strength = "schwach"

direction = "positiv" if r > 0 else "negativ"

print(f"\n=== Pearson Korrelation ===")
print(f"n  = {len(df)} Artists")
print(f"r  = {r:.4f}")
print(f"p  = {p:.4f}")
print(f"r² = {r ** 2:.4f}  ({r ** 2 * 100:.1f}% Varianz erklärt)")
print(f"→  {strength} {direction}e Korrelation")
print(f"→  {'statistisch signifikant' if p < 0.05 else 'nicht signifikant'}")

# Regressionline
slope, intercept, r_val, p_val, std_err = stats.linregress(
    df["listeners"], df["total_events"]
)

# Plot
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle(
    "F1: Last.fm Listeners vs Tour Scale (Number of Events)",
    fontsize=15, fontweight="bold", y=1.02
)

# Left plot: scatterplot
ax1 = axes[0]

ax1.scatter(
    df["listeners"], df["total_events"],
    color="steelblue", alpha=0.7, s=80, zorder=5, label="Artists"
)

# Top 15 artist label
top = df.nlargest(15, "total_events")
for _, row in top.iterrows():
    ax1.annotate(
        row["artist_name"],
        (row["listeners"], row["total_events"]),
        textcoords="offset points",
        xytext=(6, 4), fontsize=7, color="darkblue"
    )

# Trendline
x_line = np.linspace(df["listeners"].min(), df["listeners"].max(), 100)
y_line = slope * x_line + intercept
ax1.plot(x_line, y_line, color="red", linestyle="--",
         linewidth=2, label=f"Trendlinie (r={r:.3f})")

# Confidence band
n = len(df)
x_mean = df["listeners"].mean()
se = std_err * np.sqrt(
    1 / n + (x_line - x_mean) ** 2 / np.sum((df["listeners"] - x_mean) ** 2)
)
t_crit = stats.t.ppf(0.975, df=n - 2)
ax1.fill_between(
    x_line,
    y_line - t_crit * se,
    y_line + t_crit * se,
    alpha=0.15, color="red", label="95% Konfidenzband"
)

ax1.set_xlabel("Last.fm Listeners", fontsize=11)
ax1.set_ylabel("Number of Scheduled Events", fontsize=11)
ax1.set_title(
    f"Scatterplot\nr = {r:.3f} | p = {p:.4f} | n = {len(df)}",
    fontsize=11
)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{x / 1e6:.1f}M"
))
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# Right plot: distribution
ax2 = axes[1]

# Artists divided into 4 quartiles by listeners
df["quartile"] = pd.qcut(df["listeners"], q=4, labels=[
    "Q1\n(niedrig)", "Q2", "Q3", "Q4\n(hoch)"
])

quartile_means = df.groupby("quartile", observed=True)["total_events"].mean()

bars = ax2.bar(
    quartile_means.index,
    quartile_means.values,
    color=["#d4e6f1", "#7fb3d3", "#2e86c1", "#1a5276"],
    edgecolor="white", linewidth=1.5
)

# value over bars
for bar, val in zip(bars, quartile_means.values):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        f"{val:.1f}",
        ha="center", va="bottom", fontsize=10, fontweight="bold"
    )

ax2.set_xlabel("Listener Quartile", fontsize=11)
ax2.set_ylabel("Ø Anzahl Events", fontsize=11)
ax2.set_title(
    "Ø Events pro Listener-Quartil\n(Q1=wenigste Listeners, Q4=meiste)",
    fontsize=11
)
ax2.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("data/plots/f1_correlation.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n Plot gespeichert → data/plots/f1_correlation.png")

# Interpretation
print("\n=== Interpretation ===")
print(f"""
Forschungsfrage: How does the number of Last.fm listeners correlate 
with the scale of an artist's tour (number of events)?

Ergebnis:
- Pearson r = {r:.3f} → {strength} {direction}e Korrelation
- p = {p:.4f} → {'signifikant (p < 0.05)' if p < 0.05 else 'nicht signifikant (p > 0.05)'}
- r² = {r ** 2:.3f} → Last.fm listeners erklären {r ** 2 * 100:.1f}% der Varianz in Tour-Größe

Für Methodology:
Artists with more Last.fm listeners tend to schedule {'more' if r > 0 else 'fewer'} 
events. The relationship is {strength} (r = {r:.3f}) and 
{'statistically significant' if p < 0.05 else 'not statistically significant'} 
at the 0.05 level (p = {p:.4f}, n = {len(df)}).
""")
