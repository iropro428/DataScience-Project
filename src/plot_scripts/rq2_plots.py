from __future__ import annotations

from pathlib import Path
import textwrap

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib.gridspec import GridSpec
from scipy import stats


REPO_ROOT = Path(__file__).resolve().parents[2]
FINAL_DATA = REPO_ROOT / "data/processed/final_dataset.csv"
TRACK_DATA = REPO_ROOT / "data/raw/lastfm_toptracks.csv"
OUT_DIR = REPO_ROOT / "data/plots/rq2"

SELECTED_ARTISTS = ["Toto", "Chris Isaak", "Queen", "TWICE"]
CATEGORY_LABELS = ["Breit", "Moderat", "Fokussiert", "Konzentriert"]

BG = "#070b16"
PANEL = "#121a2f"
GRID = "#2a3553"
TXT = "#e8eefc"
SUBTXT = "#9aa7c7"
ACCENT = "#31c48d"
WARN = "#f59e0b"
RED = "#ef4444"


def style_axes(ax, grid_axis: str = "both") -> None:
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=TXT)
    ax.xaxis.label.set_color(TXT)
    ax.yaxis.label.set_color(TXT)
    ax.title.set_color(TXT)
    ax.grid(True, axis=grid_axis, color=GRID, alpha=0.6, linewidth=0.8)
    ax.set_axisbelow(True)


def load_f2_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not FINAL_DATA.exists():
        raise FileNotFoundError(f"Missing file: {FINAL_DATA}")
    if not TRACK_DATA.exists():
        raise FileNotFoundError(f"Missing file: {TRACK_DATA}")

    df = pd.read_csv(FINAL_DATA)
    tracks = pd.read_csv(TRACK_DATA)

    numeric_cols = [
        "top5_share", "top3_share", "top1_share", "hhi",
        "events_last_year", "total_events", "listeners", "total_track_plays",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    tracks["rank"] = pd.to_numeric(tracks["rank"], errors="coerce")
    tracks["playcount"] = pd.to_numeric(tracks["playcount"], errors="coerce")

    df_f2 = df.dropna(subset=["artist_name", "top5_share", "events_last_year"]).copy()
    df_f2 = df_f2.sort_values(["events_last_year", "top5_share"], ascending=[False, True]).reset_index(drop=True)
    return df_f2, tracks


def compute_stats(df_f2: pd.DataFrame) -> dict:
    x = df_f2["top5_share"]
    y = df_f2["events_last_year"]
    pearson_r, pearson_p = stats.pearsonr(x, y)
    slope, intercept, _, _, _ = stats.linregress(x, y)
    spearman_rho, spearman_p = stats.spearmanr(x, y)

    df_f2["cat4"] = pd.qcut(
        df_f2["top5_share"],
        q=4,
        labels=CATEGORY_LABELS,
        duplicates="drop",
    )
    kw_groups = [
        grp["events_last_year"].dropna().values
        for _, grp in df_f2.groupby("cat4", observed=True)
    ]
    kw_h, kw_p = stats.kruskal(*kw_groups)

    return {
        "n": len(df_f2),
        "pearson_r": pearson_r,
        "pearson_p": pearson_p,
        "r2": pearson_r ** 2,
        "slope": slope,
        "intercept": intercept,
        "spearman_rho": spearman_rho,
        "spearman_p": spearman_p,
        "kw_h": kw_h,
        "kw_p": kw_p,
    }


def add_header(fig, title: str, subtitle: str) -> None:
    fig.patch.set_facecolor(BG)
    fig.suptitle(title, color=TXT, fontsize=17, fontweight="bold", x=0.06, ha="left", y=0.97)
    fig.text(0.06, 0.92, subtitle, color=SUBTXT, fontsize=10, ha="left")


def make_scatter_plot(df_f2: pd.DataFrame, stats_dict: dict) -> Path:
    out = OUT_DIR / "rq2_scatter.png"
    fig, ax = plt.subplots(figsize=(13, 8), facecolor=BG)
    style_axes(ax)
    add_header(
        fig,
        "RQ2 — Streaming Concentration vs. Touring Intensity",
        "X = Top-5 share of total Last.fm top-track playcount, Y = events in the last 12 months (Ticketmaster).",
    )

    rng = np.random.default_rng(42)
    y_jitter = df_f2["events_last_year"] + rng.normal(0, 0.035, len(df_f2))
    norm = mcolors.Normalize(vmin=df_f2["top5_share"].min(), vmax=df_f2["top5_share"].max())
    scatter = ax.scatter(
        df_f2["top5_share"],
        y_jitter,
        c=df_f2["top5_share"],
        cmap="RdYlGn_r",
        norm=norm,
        s=85,
        alpha=0.92,
        edgecolor="#d9e2ff",
        linewidth=0.6,
    )

    x_line = np.linspace(df_f2["top5_share"].min(), df_f2["top5_share"].max(), 200)
    y_line = stats_dict["slope"] * x_line + stats_dict["intercept"]
    ax.plot(x_line, y_line, color=ACCENT, linewidth=2.3, label="OLS trend line")

    labels_to_show = [a for a in SELECTED_ARTISTS if a in set(df_f2["artist_name"])]
    for artist in labels_to_show:
        row = df_f2.loc[df_f2["artist_name"] == artist].iloc[0]
        ax.annotate(
            artist,
            (row["top5_share"], row["events_last_year"]),
            xytext=(7, 7),
            textcoords="offset points",
            fontsize=9,
            color=TXT,
        )

    ax.set_xlabel("Share of top 5 tracks in total playcount (%)", fontsize=11)
    ax.set_ylabel("Events in last 12 months", fontsize=11)
    ax.set_xlim(df_f2["top5_share"].min() - 3, df_f2["top5_share"].max() + 3)
    ax.set_ylim(df_f2["events_last_year"].min() - 0.15, df_f2["events_last_year"].max() + 0.25)
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=TXT)

    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.ax.yaxis.set_tick_params(color=TXT)
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=TXT)
    cbar.outline.set_edgecolor(GRID)
    cbar.set_label("Top-5 share (%)", color=TXT)

    sig_txt = "significant" if stats_dict["pearson_p"] < 0.05 else "not significant"
    stat_box = (
        f"n = {stats_dict['n']}\n"
        f"Pearson r = {stats_dict['pearson_r']:.3f}\n"
        f"R² = {stats_dict['r2']:.1%}\n"
        f"p = {stats_dict['pearson_p']:.4f}\n"
        f"{sig_txt}"
    )
    ax.text(
        0.02,
        0.96,
        stat_box,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=10,
        color=TXT,
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#0e1425", edgecolor=GRID, alpha=0.98),
    )

    fig.tight_layout(rect=[0, 0, 1, 0.9])
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out


def make_boxplot(df_f2: pd.DataFrame, stats_dict: dict) -> Path:
    out = OUT_DIR / "rq2_boxplot.png"
    fig, ax = plt.subplots(figsize=(12, 8), facecolor=BG)
    style_axes(ax, grid_axis="y")
    add_header(
        fig,
        "RQ2 — Touring Intensity by Streaming-Concentration Category",
        "Artists are split into four equally sized concentration groups using top5_share quartiles.",
    )

    grouped = [
        df_f2.loc[df_f2["cat4"] == label, "events_last_year"].dropna().values
        for label in CATEGORY_LABELS
    ]

    colors = ["#22c55e", "#93c5fd", "#fbbf24", "#ef4444"]
    bp = ax.boxplot(grouped, patch_artist=True, tick_labels=CATEGORY_LABELS, widths=0.55)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.28)
        patch.set_edgecolor(color)
        patch.set_linewidth(2)
    for element in ["whiskers", "caps", "medians"]:
        for item in bp[element]:
            item.set_color(TXT)
            item.set_linewidth(1.5)

    rng = np.random.default_rng(7)
    for i, (label, color) in enumerate(zip(CATEGORY_LABELS, colors), start=1):
        vals = df_f2.loc[df_f2["cat4"] == label, "events_last_year"].dropna().values
        xs = i + rng.normal(0, 0.04, len(vals))
        ax.scatter(xs, vals, color=color, s=55, alpha=0.9, edgecolor="#d9e2ff", linewidth=0.5)
        if len(vals):
            ax.text(i, vals.min() - 0.12, f"n={len(vals)}", ha="center", va="top", color=SUBTXT, fontsize=10)

    ax.set_xlabel("Streaming concentration category", fontsize=11)
    ax.set_ylabel("Events in last 12 months", fontsize=11)
    ax.set_ylim(df_f2["events_last_year"].min() - 0.18, df_f2["events_last_year"].max() + 0.25)

    kw_text = (
        f"Kruskal-Wallis H = {stats_dict['kw_h']:.2f}\n"
        f"p = {stats_dict['kw_p']:.4f}\n"
        f"{'significant' if stats_dict['kw_p'] < 0.05 else 'not significant'}"
    )
    ax.text(
        0.02,
        0.96,
        kw_text,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=10,
        color=TXT,
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#0e1425", edgecolor=GRID, alpha=0.98),
    )

    fig.tight_layout(rect=[0, 0, 1, 0.9])
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out


def make_profile_plot(df_f2: pd.DataFrame, tracks: pd.DataFrame) -> Path:
    out = OUT_DIR / "rq2_artist_profiles.png"

    available = [artist for artist in SELECTED_ARTISTS if artist in set(df_f2["artist_name"]) and artist in set(tracks["artist_name"])]
    if len(available) < 2:
        available = df_f2.nlargest(4, "top5_share")["artist_name"].tolist()[:4]

    fig = plt.figure(figsize=(15, 9), facecolor=BG)
    gs = GridSpec(2, 1, height_ratios=[4.0, 1.3], hspace=0.18)
    ax = fig.add_subplot(gs[0])
    ax_tbl = fig.add_subplot(gs[1])
    style_axes(ax, grid_axis="y")
    ax_tbl.set_facecolor(PANEL)
    ax_tbl.axis("off")

    add_header(
        fig,
        "RQ2 — Streaming Profiles of Selected Artists",
        "Stacked bars show how strongly total top-track playcount is concentrated in the first five tracks.",
    )

    top_colors = ["#22c55e", "#34d399", "#4ade80", "#86efac", "#bbf7d0"]
    rest_color = "#334155"
    legend_labels = []
    metric_rows = []

    x_positions = np.arange(len(available))
    for i, artist in enumerate(available):
        artist_tracks = tracks.loc[tracks["artist_name"] == artist].sort_values("rank").head(20).copy()
        total = artist_tracks["playcount"].sum()
        artist_tracks["share_pct"] = np.where(total > 0, artist_tracks["playcount"] / total * 100, 0)
        top5 = artist_tracks.head(5)
        bottom = 0.0

        for j, (_, row) in enumerate(top5.iterrows()):
            share = row["share_pct"]
            ax.bar(i, share, bottom=bottom, color=top_colors[j], edgecolor=BG, linewidth=1.0)
            if share >= 4.0:
                ax.text(i, bottom + share / 2, f"{share:.0f}%", ha="center", va="center", fontsize=9, color=BG, fontweight="bold")
            bottom += share
            if i == 0:
                legend_labels.append((f"#{int(row['rank'])} {row['track_name']}", top_colors[j]))

        rest_share = max(0.0, 100 - bottom)
        ax.bar(i, rest_share, bottom=bottom, color=rest_color, edgecolor=BG, linewidth=1.0)

        meta = df_f2.loc[df_f2["artist_name"] == artist].iloc[0]
        metric_rows.append([
            artist,
            f"{meta['top5_share']:.1f}",
            f"{meta['top3_share']:.1f}",
            f"{meta['top1_share']:.1f}",
            f"{meta['events_last_year']:.0f}",
            f"{meta['total_events']:.0f}",
        ])

    ax.set_xticks(x_positions)
    ax.set_xticklabels(available, rotation=12)
    ax.set_ylabel("Share of total top-track playcount (%)", fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 10))

    legend_handles = [plt.Rectangle((0, 0), 1, 1, color=color) for _, color in legend_labels]
    legend_names = [name for name, _ in legend_labels]
    legend_handles.append(plt.Rectangle((0, 0), 1, 1, color=rest_color))
    legend_names.append("Ranks 6–20 combined")
    ax.legend(
        legend_handles,
        legend_names,
        ncol=3,
        fontsize=8,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        facecolor=PANEL,
        edgecolor=GRID,
        labelcolor=TXT,
    )

    table = ax_tbl.table(
        cellText=metric_rows,
        colLabels=["Artist", "Top-5 %", "Top-3 %", "Top-1 %", "Events/yr", "Total events"],
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_linewidth(1.0)
        if row == 0:
            cell.set_facecolor("#1b2744")
            cell.get_text().set_color(TXT)
            cell.get_text().set_weight("bold")
        else:
            cell.set_facecolor(PANEL)
            cell.get_text().set_color(TXT)

    fig.tight_layout(rect=[0, 0, 1, 0.9])
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out


def make_summary_figure(df_f2: pd.DataFrame, stats_dict: dict) -> Path:
    out = OUT_DIR / "rq2_summary.png"
    fig = plt.figure(figsize=(13, 7.5), facecolor=BG)
    add_header(
        fig,
        "RQ2 — Statistical Summary",
        "Compact summary for slides or the written report.",
    )

    ax_table = fig.add_axes([0.05, 0.36, 0.9, 0.48])
    ax_text = fig.add_axes([0.05, 0.08, 0.9, 0.22])
    ax_table.set_facecolor(PANEL)
    ax_text.set_facecolor(PANEL)
    ax_table.axis("off")
    ax_text.axis("off")

    summary_rows = [
        ["Artists with complete F2 data", f"{len(df_f2)}"],
        ["Concentration metric", "Top-5 share of total track playcount"],
        ["Touring metric", "Events in last 12 months"],
        ["Pearson r", f"{stats_dict['pearson_r']:.3f}"],
        ["R²", f"{stats_dict['r2']:.1%}"],
        ["p-value", f"{stats_dict['pearson_p']:.4f}"],
        ["Spearman rho", f"{stats_dict['spearman_rho']:.3f}"],
        ["Kruskal-Wallis p", f"{stats_dict['kw_p']:.4f}"],
        ["Significant?", "Yes" if stats_dict['pearson_p'] < 0.05 else "No"],
    ]

    table = ax_table.table(
        cellText=summary_rows,
        colLabels=["Metric", "Value"],
        loc="center",
        cellLoc="left",
        colLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.6)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_linewidth(1.0)
        if row == 0:
            cell.set_facecolor("#1b2744")
            cell.get_text().set_color(TXT)
            cell.get_text().set_weight("bold")
        else:
            cell.set_facecolor(PANEL)
            cell.get_text().set_color(TXT)

    if stats_dict["pearson_p"] < 0.05:
        conclusion = (
            f"There is a statistically significant relationship between streaming concentration and touring intensity "
            f"(r = {stats_dict['pearson_r']:.3f}, p = {stats_dict['pearson_p']:.4f})."
        )
        edge = ACCENT
    else:
        conclusion = (
            f"The relationship is weak and not statistically significant "
            f"(r = {stats_dict['pearson_r']:.3f}, R² = {stats_dict['r2']:.1%}, p = {stats_dict['pearson_p']:.4f}). "
            f"In this sample, concentration on a few top tracks does not meaningfully predict events per year."
        )
        edge = WARN

    note = (
        "Method note: top5_share is computed from the Last.fm top 20 tracks per artist, so it approximates concentration "
        "within the visible top-catalog rather than the full catalog."
    )
    wrapped = textwrap.fill(conclusion, width=120)
    wrapped_note = textwrap.fill(note, width=120)

    ax_text.text(
        0.02,
        0.72,
        "Answer to RQ2",
        color=TXT,
        fontsize=13,
        fontweight="bold",
        transform=ax_text.transAxes,
    )
    ax_text.text(
        0.02,
        0.38,
        wrapped,
        color=TXT,
        fontsize=11,
        transform=ax_text.transAxes,
        bbox=dict(boxstyle="round,pad=0.55", facecolor="#0e1425", edgecolor=edge, linewidth=1.4),
    )
    ax_text.text(0.02, 0.05, wrapped_note, color=SUBTXT, fontsize=9.5, transform=ax_text.transAxes)

    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out


def save_summary_csv(df_f2: pd.DataFrame, stats_dict: dict) -> Path:
    out = OUT_DIR / "rq2_summary_stats.csv"
    summary = pd.DataFrame(
        {
            "metric": [
                "artists_with_complete_f2_data",
                "pearson_r",
                "r_squared",
                "pearson_p",
                "spearman_rho",
                "spearman_p",
                "kruskal_h",
                "kruskal_p",
                "mean_top5_share",
                "mean_events_last_year",
            ],
            "value": [
                len(df_f2),
                stats_dict["pearson_r"],
                stats_dict["r2"],
                stats_dict["pearson_p"],
                stats_dict["spearman_rho"],
                stats_dict["spearman_p"],
                stats_dict["kw_h"],
                stats_dict["kw_p"],
                df_f2["top5_share"].mean(),
                df_f2["events_last_year"].mean(),
            ],
        }
    )
    summary.to_csv(out, index=False)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df_f2, tracks = load_f2_data()
    stats_dict = compute_stats(df_f2)

    outputs = [
        make_scatter_plot(df_f2, stats_dict),
        make_boxplot(df_f2, stats_dict),
        make_profile_plot(df_f2, tracks),
        make_summary_figure(df_f2, stats_dict),
        save_summary_csv(df_f2, stats_dict),
    ]

    print("Created files:")
    for path in outputs:
        print(f" - {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
