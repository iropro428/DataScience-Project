import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import os

import sys as _sys, os as _os

from components.styles import apply_styles
from components.navbar import render_navbar
from components.glossary import apply_glossary_styles, tt
from components.util import hex_rgba

st.set_page_config(
    page_title="F1 – Listeners vs Tour Scale",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
apply_styles()
render_navbar()
apply_glossary_styles()

# CSS


# Header 
st.markdown("""
<div class="page-header">
    <h1>🎟️ Streaming &amp; Ticket Power</h1>
    <p>How strongly is digital popularity on Last.fm related to the scale and intensity of touring?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#161c2d;border:1px solid #232840;border-radius:14px;
    padding:24px 28px;margin-bottom:28px;">
    <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;
        letter-spacing:.12em;color:#475569 !important;margin-bottom:14px;">
        Table of contents — Research questions
    </div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <a href="#frage-1" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">1</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                How does the number of Last.fm listeners correlate with the scale of an artist's tour, measured by the number of events scheduled?
            </span>
        </a>
        <a href="#frage-2" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">2</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                How does the concentration of an artist's streaming activity on a few top tracks relate to the intensity of their touring, measured by events per year?
            </span>
        </a>
        <a href="#frage-3" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">3</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                How do current Last.fm listener counts differ between artists who appeared in Spotify Weekly Charts (Feb 2023–Feb 2026) and those who did not?
            </span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="frage-1"></div>', unsafe_allow_html=True)


# Load Data 
@st.cache_data
def load_data():
    path = "data/processed/final_dataset.csv"
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df = df.dropna(subset=["listeners", "total_events"])
    df = df[df["total_events"] > 0].copy()
    return df


df = load_data()

if df is None:
    st.error("Dataset not found. Please run the collection scripts first.")
    st.code("python scripts/collect_artists_lastfm.py\npython scripts/collect_ticketmaster.py\npython scripts/join_data.py")
    st.stop()


# Genre Helper
def extract_genres(tags_str):
    if pd.isna(tags_str):
        return []
    return [t.strip().lower() for t in str(tags_str).split(",")]


all_genres = set()
for tags in df.get("tags", pd.Series(dtype=str)).dropna():
    for g in extract_genres(tags):
        if len(g) > 2:
            all_genres.add(g)
top_genres = sorted(list(all_genres))[:50]

# ══════════════════════════════════════════════════════
# RESEARCH QUESTION 1
# ══════════════════════════════════════════════════════
st.markdown("""
<div class="rq-box">
    <h3>🔬 Research Question 1</h3>
    <p>How does the number of Last.fm listeners correlate with the scale of an artist's tour,
    measured by the number of events scheduled?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**What are we measuring?**
We examine whether artists with more Last.fm listeners also tend to perform more live concerts.
The Last.fm listener count indicates how many unique users have listened to an artist —
a recognized academic proxy for digital popularity.
Tour scale = total number of Ticketmaster events from 2022–2026.

**Why is this relevant?**  
If digital popularity predicts live activity, this supports the idea that streaming platforms
can serve as a planning basis for the live music industry.
""")

st.divider()

# ══════════════════════════════════════════════════════
# GRAPH 1 — Scatterplot
# ══════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 1 — Scatterplot: Last.fm listeners vs. number of events</div>',
            unsafe_allow_html=True)

st.markdown("""
A **scatterplot** directly shows the relationship between two numerical variables.
Each point = one artist. The **trend line (OLS regression)** shows the direction of the correlation.
The shaded band = 95% confidence interval.
Use the filters to explore subsets of the data and see how r changes.
""")

# Filter Controls
c1, c2 = st.columns(2)
with c1:
    listener_range = st.slider(
        "🎧 Listener range (Last.fm)",
        min_value=int(df["listeners"].min()),
        max_value=int(df["listeners"].max()),
        value=(int(df["listeners"].min()), int(df["listeners"].max())),
        key="g1_lr"
    )
with c2:
    event_max = st.slider(
        "🎟️ Max. events (remove outliers)",
        min_value=5,
        max_value=int(df["total_events"].max()),
        value=int(df["total_events"].max()),
        key="g1_em"
    )

c3, c4 = st.columns([3, 1])
with c3:
    selected_genres = st.multiselect(
        "🎵 Genre filter (empty = all)",
        options=top_genres, default=[], key="g1_genres"
    )
with c4:
    show_labels = st.checkbox("Show artist names", value=False, key="g1_lbl")

# Apply filters
df1 = df[
    (df["listeners"] >= listener_range[0]) &
    (df["listeners"] <= listener_range[1]) &
    (df["total_events"] <= event_max)
    ].copy()

if selected_genres and "tags" in df1.columns:
    df1 = df1[df1["tags"].apply(lambda x: any(
        g in extract_genres(x) for g in selected_genres
    ))]

# Stats
if len(df1) >= 5:
    r, p = stats.pearsonr(df1["listeners"], df1["total_events"])
    r2 = r ** 2
    strength = "strong" if abs(r) >= 0.7 else "moderate" if abs(r) >= 0.4 else "weak"
    direction = "positive" if r > 0 else "negative"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("n artists", len(df1))
    m2.metric("Pearson r", f"{r:.3f}")
    m3.metric("R² (variance explained)", f"{r2:.1%}")
    m4.metric("p-value", f"{p:.4f}",
              delta="significant " if p < 0.05 else "not significant ",
              delta_color="normal" if p < 0.05 else "inverse")

    # Plot 
    hover = {"listeners": ":,", "total_events": True}
    if "tags" in df1.columns:
        hover["tags"] = True

    # Manuelle OLS-Trendlinie
    _c1 = np.polyfit(df1["listeners"], df1["total_events"], 1)
    _x1 = np.linspace(df1["listeners"].min(), df1["listeners"].max(), 200)
    _y1 = np.polyval(_c1, _x1)

    fig1 = px.scatter(
        df1,
        x="listeners",
        y="total_events",
        hover_name="artist_name",
        hover_data=hover,
        color="total_events",
        color_continuous_scale="Viridis",
        text="artist_name" if show_labels else None,
        labels={
            "listeners": "Last.fm listeners",
            "total_events": "Number of scheduled events",
            "tags": "Genre tags"
        },
        title=f"Last.fm listeners vs. tour scale  |  r = {r:.3f}  |  n = {len(df1)} artists",
        template="plotly_dark"
    )
    fig1.add_trace(go.Scatter(
        x=_x1, y=_y1, mode="lines", name="OLS",
        line=dict(color="#1DB954", width=2.5),
        hoverinfo="skip",
    ))
    fig1.update_traces(
        marker=dict(size=9, opacity=0.8, line=dict(width=0.5, color="white")),
        selector=dict(mode="markers")
    )
    fig1.update_traces(
        line=dict(color="#1DB954", width=2.5),
        selector=dict(mode="lines")
    )
    if show_labels:
        fig1.update_traces(
            textposition="top center",
            textfont=dict(size=8, color="white"),
            selector=dict(mode="markers+text")
        )
    fig1.update_layout(
        height=520,
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#333", tickformat=","),
        yaxis=dict(gridcolor="#333")
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Interpretation 
    st.markdown(f"""
    <div class="insight-card">
        <h4>📊 Statistical result</h4>
        <p>
        The Pearson correlation coefficient is <strong style="color:#1DB954">r = {r:.3f}</strong>
        — this is a <strong>{strength} {direction} correlation</strong> between Last.fm listeners 
        and tour scale. The R² value of <strong style="color:#1DB954">{r2:.1%}</strong> means 
        that the listener count explains {r2:.1%} of the variance in the number of events.
        The result is <strong>{"statistically significant " if p < 0.05 else "not statistically significant "}</strong>
        (p = {p:.4f}, n = {len(df1)}).
        </p>
    </div>
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>
        Artists with more Last.fm listeners tend to perform 
        {"more" if r > 0 else "fewer"} concerts.
        {"This supports the hypothesis that digital popularity is related to live activity."
    if r > 0 and p < 0.05 and abs(r) >= 0.4 else
    "However, the relationship is weak — digital popularity alone only partially predicts tour scale."
    if abs(r) < 0.4 else
    "The relationship is moderate — other factors such as genre, management, and budget also play an important role."}
        <br><br>
        <strong>Note:</strong> Correlation does not imply causation. A high listener count 
        could also be a result of past tours, not only a predictor of future ones.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("Too few data points after filtering. Please adjust the filters.")

st.divider()

# ══════════════════════════════════════════════════════
# GRAPH 2 — Bar Chart (Quartile)
# ══════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 2 — Avg. events per listener quartile</div>',
            unsafe_allow_html=True)

st.markdown("""
To show the pattern more clearly, we divide artists into equally sized **groups based on listener count**.
The **bar chart** shows the average number of events per group.
Unlike the scatterplot, this view reduces noise and makes structural trends
immediately visible — ideal for a summary statement.
""")

qa, qb = st.columns([1, 3])
with qa:
    n_groups = st.select_slider(
        "Number of groups",
        options=[3, 4, 5, 6, 8, 10],
        value=4, key="g2_ng"
    )
    agg = st.radio("Aggregation", ["Mean", "Median"], index=0, key="g2_agg")

try:
    df2 = df.copy()
    labels = [f"G{i + 1}" for i in range(n_groups)]
    df2["group"] = pd.qcut(df2["listeners"], q=n_groups, labels=labels, duplicates="drop")
    agg_fn = "mean" if agg == "Mean" else "median"

    grouped = df2.groupby("group", observed=True).agg(
        avg_events=("total_events", agg_fn),
        n_artists=("artist_name", "count"),
        avg_listeners=("listeners", "mean")
    ).reset_index()

    fig2 = go.Figure(go.Bar(
        x=grouped["group"].astype(str),
        y=grouped["avg_events"],
        text=[f"{v:.1f}" for v in grouped["avg_events"]],
        textposition="outside",
        textfont=dict(color="white", size=13),
        marker=dict(
            color=list(range(len(grouped))),
            colorscale=[[0, "#0d2b1a"], [0.5, "#1DB954"], [1, "#00ff88"]],
            line=dict(width=0)
        ),
        customdata=grouped[["n_artists", "avg_listeners"]].values,
        hovertemplate=(
            "<b>Group %{x}</b><br>"
            f"{agg} events: %{{y:.1f}}<br>"
            "Artists: %{customdata[0]}<br>"
            "Avg. listeners: %{customdata[1]:,.0f}<extra></extra>"
        )
    ))
    fig2.update_layout(
        title=f"{agg} number of events per listener group  ({n_groups} groups, G1=fewest listeners)",
        xaxis_title="Listener group",
        yaxis_title=f"{agg} events",
        template="plotly_dark",
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"), height=400,
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        showlegend=False
    )
    with qb:
        st.plotly_chart(fig2, use_container_width=True)

    g1_val = grouped.iloc[0]["avg_events"]
    gn_val = grouped.iloc[-1]["avg_events"]
    diff = gn_val - g1_val
    st.markdown(f"""
    <div class="insight-card">
        <h4>📈 Group comparison</h4>
        <p>
        Artists in the group with the <strong>highest number of listeners</strong> perform on average
        <strong style="color:#1DB954">{gn_val:.1f} events</strong>, 
        while the group with the fewest listeners performs only <strong>{g1_val:.1f} events</strong> — 
        a difference of <strong style="color:#1DB954">{diff:+.1f} events</strong>.
        {"The pattern is consistent across all groups and confirms a monotonic relationship." if diff > 2 else
    "The difference between the groups is small — listener count is not a strong predictor of tour scale."}
        </p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.warning(f"Grouping failed: {e}")

st.divider()

# ══════════════════════════════════════════════════════
# GRAPH 3 — Histogram (Distribution)
# ══════════════════════════════════════════════════════
st.markdown('<div class="section-title">📉 Graph 3 — Distribution of Last.fm listeners</div>',
            unsafe_allow_html=True)

st.markdown("""
Before interpreting correlations, we need to understand the **data distribution**.
A **histogram** shows how many artists fall into which listener ranges.
A strongly skewed distribution (a few superstars, many mid-tier artists) affects
the Pearson coefficient and must be considered in the interpretation.
""")

ha, hb = st.columns([1, 3])
with ha:
    n_bins = st.slider("Number of bins", 10, 80, 30, key="g3_bins")
    log_x = st.checkbox("Logarithmic X-axis", value=False, key="g3_log")
    show_rug = st.checkbox("Individual points (rug plot)", value=False, key="g3_rug")

with hb:
    x_data = np.log10(df["listeners"] + 1) if log_x else df["listeners"]
    x_lab = "log₁₀(Last.fm listeners)" if log_x else "Last.fm listeners"

    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(
        x=x_data, nbinsx=n_bins, name="Artists",
        marker=dict(color="#1DB954", opacity=0.8,
                    line=dict(width=0.5, color="#0e0e0e")),
        hovertemplate="Listeners: %{x}<br>Count: %{y}<extra></extra>"
    ))
    if show_rug:
        fig3.add_trace(go.Scatter(
            x=x_data, y=[-2] * len(x_data), mode="markers",
            marker=dict(symbol="line-ns", size=8, color="#1DB954", opacity=0.3,
                        line=dict(width=1, color="#1DB954")),
            name="Individual artists", hoverinfo="skip"
        ))

    med = float(np.median(x_data))
    avg = float(np.mean(x_data))
    fig3.add_vline(x=med, line=dict(color="#f0c040", width=2, dash="dash"),
                   annotation_text=f"Median: {10 ** med:,.0f}" if log_x else f"Median: {med:,.0f}",
                   annotation_font_color="#f0c040")
    fig3.add_vline(x=avg, line=dict(color="#ff6b6b", width=2, dash="dot"),
                   annotation_text=f"Mean: {10 ** avg:,.0f}" if log_x else f"Mean: {avg:,.0f}",
                   annotation_font_color="#ff6b6b", annotation_position="top left")

    fig3.update_layout(
        title="Distribution of Last.fm listeners across all artists",
        xaxis_title=x_lab, yaxis_title="Number of artists",
        template="plotly_dark",
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"), height=380,
        xaxis=dict(gridcolor="#333", tickformat=","),
        yaxis=dict(gridcolor="#333"), showlegend=False
    )
    st.plotly_chart(fig3, use_container_width=True)

skew = float(pd.Series(df["listeners"]).skew())
st.markdown(f"""<div class="insight-card">
<h4>📐 Distribution analysis</h4>
<p>
The distribution is <strong>{"strongly" if abs(skew) > 1 else "moderately"} 
{"right-skewed" if skew > 0 else "left-skewed"}</strong> (skewness = {skew:.2f}).
This is typical for popularity data — a few global superstars dominate,
while the majority of artists have far fewer listeners.
{"The logarithmic transformation (checkbox above) normalizes this distribution." if abs(skew) > 1 else ""}
<br/>
<strong>Implication for the correlation:</strong>
A few outliers (superstars) can strongly influence Pearson r.
Use the slider in Graph 1 to remove extreme outliers and observe
how r changes — this shows the robustness of the correlation.
</p>
</div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════
# SUMMARY F1
# ══════════════════════════════════════════════════════
st.markdown('<div class="section-title">Summary — Research Question 1</div>',
            unsafe_allow_html=True)

if len(df) >= 5:
    r_all, p_all = stats.pearsonr(df["listeners"], df["total_events"])
    r2_all = r_all ** 2
    st_all = "strong" if abs(r_all) >= 0.7 else "moderate" if abs(r_all) >= 0.4 else "weak"

    st.markdown(f"""
    | Metric | Value |
    |--------|------|
    | Sample size (n) | {len(df)} artists |
    | Pearson r | {r_all:.3f} |
    | R² | {r2_all:.1%} |
    | p-value | {p_all:.4f} |
    | Statistically significant | {'Yes (p < 0.05) ' if p_all < 0.05 else 'No (p ≥ 0.05) '} |
    | Correlation strength | {st_all.capitalize()} |
    """)

    answer = (
            f"There is a **{st_all} {'positive' if r_all > 0 else 'negative'} correlation** "
            f"(r = {r_all:.3f}) between Last.fm listener count and tour scale. "
            f"The listener count explains about **{r2_all:.1%}** of the variance in the number of scheduled events. "
            + ("This confirms that digital popularity is related to real-world tour planning."
               if p_all < 0.05 and r_all > 0.3 else
               "However, the relationship is statistically weak — additional factors must be taken into account.")
    )
    st.markdown(f"""<div class="insight-card">
        <h4>🎯 Answer to Research Question 1</h4>
        <p>{answer}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("""<div class="methodology-note">
    <p>
    <strong>Methodological note:</strong> Last.fm listener counts were collected as a static snapshot (March 2026),
    because Spotify disabled follower and popularity fields for development-mode apps in February 2026.
    Ticketmaster event data covers January 2022–December 2026. The analysis is restricted to artists
    with at least one Ticketmaster event and available Last.fm data.
    </p>
</div>""", unsafe_allow_html=True)

st.markdown('<div id="frage-2"></div>', unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════
# RESEARCH QUESTION 2 — Streaming concentration vs. tour intensity
# ══════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown("""<div class="rq-box">
    <h3>🔬 Research Question 2</h3>
    <p>How does the concentration of an artist's streaming activity on a few top tracks
    relate to the intensity of their touring, measured by events per year?</p>
</div>""", unsafe_allow_html=True)

st.markdown("""**What are we measuring?**

**Streaming concentration** = share of the top 5 tracks in an artist's total playcount.
A high value (e.g. 80%) means that almost all streams come from 5 songs — a classic
"one-hit wonder" pattern or a very narrow fan focus.
A low value (e.g. 30%) means that streams are distributed more evenly across many tracks
— indicating a broader and deeper catalog audience.

**Tour intensity** = number of events in the last year (Ticketmaster, last 12 months).

**Hypothesis:** Artists with a broad catalog (low concentration) tour more intensively,
because they have a more loyal core audience that returns regularly. Artists with
high concentration rely on viral hits — their live audience is less stable.
""")

# prove data
f2_required = ["top5_share", "events_last_year"]
f2_missing = [c for c in f2_required if c not in df.columns]

if f2_missing:
    st.error(f"Missing columns: {f2_missing}")
    st.code("""
# Execution order:
python scripts/collect_toptracks.py    # Fetch Last.fm top tracks
python scripts/join_data.py            # Calculate concentration + join
    """)
    st.stop()

df2 = df.dropna(subset=["top5_share", "events_last_year"]).copy()
df2["top5_share"] = pd.to_numeric(df2["top5_share"], errors="coerce")
df2["events_last_year"] = pd.to_numeric(df2["events_last_year"], errors="coerce")
df2 = df2.dropna(subset=["top5_share", "events_last_year"])

n_f2 = len(df2)
pct_cov_f2 = n_f2 / len(df) * 100

st.info(f"📊 {n_f2} artists with complete F2 data ({pct_cov_f2:.0f}% of the dataset)")

if n_f2 < 10:
    st.warning("Too few data points. Please run `collect_toptracks.py`.")
    st.stop()

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F2 — GRAPH 1: Scatterplot top5_share vs events_last_year
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 1 — Scatterplot: Streaming concentration vs. tour intensity</div>',
            unsafe_allow_html=True
            )
st.markdown("""Each point = one artist. X-axis = top-5 share (concentration), Y-axis =
events in the last year (tour intensity). The OLS trend line shows the direction
of the relationship. Hover over points for artist details.""")

sc1, sc2, sc3 = st.columns([2, 1, 1])
with sc1:
    conc_metric = st.radio(
        "Concentration metric (X-axis)",
        ["top5_share", "top3_share", "top1_share", "hhi"],
        index=0,
        horizontal=True,
        key="f2s_metric"
    )
    metric_labels = {
        "top5_share": "Share of top 5 tracks in total playcount (%)",
        "top3_share": "Share of top 3 tracks in total playcount (%)",
        "top1_share": "Share of track #1 in total playcount (%)",
        "hhi": "Herfindahl index (concentration measure 0–10000)",
    }
with sc2:
    log_y_s = st.checkbox("Log Y (events)", value=False, key="f2s_logy")
    show_names_s = st.checkbox("Show names", value=False, key="f2s_names")
with sc3:
    ev_max = st.slider(
        "Max. events/year",
        5, int(df2["events_last_year"].max()) + 5,
        int(df2["events_last_year"].quantile(0.97)),
        key="f2s_evmax"
    )

sel_genres_f2 = st.multiselect(
    "🎵 Genre filter", options=top_genres, default=[], key="f2s_genres"
)

# prove metric
if conc_metric not in df2.columns:
    st.warning(f"Metric `{conc_metric}` not in dataset — only top5_share is available.")
    conc_metric = "top5_share"

df2f = df2[df2["events_last_year"] <= ev_max].copy()
df2f = df2f.dropna(subset=[conc_metric])

if sel_genres_f2 and "tags" in df2f.columns:
    df2f = df2f[df2f["tags"].apply(
        lambda x: any(g in extract_genres(x) for g in sel_genres_f2)
    )]

if len(df2f) >= 5:
    x_vals = df2f[conc_metric]
    y_vals = np.log10(df2f["events_last_year"] + 1) if log_y_s else df2f["events_last_year"]

    r_f2, p_f2 = stats.pearsonr(x_vals, y_vals)
    r2_f2 = r_f2 ** 2
    strength_f2 = "strong" if abs(r_f2) >= 0.7 else "moderate" if abs(r_f2) >= 0.4 else "weak"
    direction_f2 = "negative" if r_f2 < 0 else "positive"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("n artists", len(df2f))
    m2.metric("Pearson r", f"{r_f2:.3f}")
    m3.metric("R²", f"{r2_f2:.1%}")
    m4.metric("p-value", f"{p_f2:.4f}",
              delta="significant " if p_f2 < 0.05 else "not significant ",
              delta_color="normal" if p_f2 < 0.05 else "inverse")

    plot_df2 = df2f.copy()
    plot_df2["y_plot"] = y_vals.values

    hover_f2 = {
        conc_metric: ":.1f",
        "events_last_year": True,
        "listeners": ":,",
    }
    if "tags" in plot_df2.columns:
        hover_f2["tags"] = True

    # Manuel OLS-Trendline
    _c_sc = np.polyfit(plot_df2[conc_metric], plot_df2["y_plot"], 1)
    _x_sc = np.linspace(plot_df2[conc_metric].min(), plot_df2[conc_metric].max(), 200)
    _y_sc = np.polyval(_c_sc, _x_sc)

    fig_sc = px.scatter(
        plot_df2,
        x=conc_metric,
        y="y_plot",
        hover_name="artist_name",
        hover_data=hover_f2,
        color=conc_metric,
        color_continuous_scale="RdYlGn_r",
        text="artist_name" if show_names_s else None,
        labels={
            conc_metric: metric_labels.get(conc_metric, conc_metric),
            "y_plot": f"{'log₁₀(' if log_y_s else ''}Events last year{')' if log_y_s else ''}",
        },
        title=(
            f"Streaming concentration vs. tour intensity  "
            f"|  r = {r_f2:.3f}  |  n = {len(df2f)}"
        ),
        template="plotly_dark"
    )
    fig_sc.add_trace(go.Scatter(
        x=_x_sc, y=_y_sc, mode="lines", name="OLS",
        line=dict(color="#1DB954", width=2.5),
        hoverinfo="skip",
    ))
    fig_sc.update_traces(
        marker=dict(size=10, opacity=0.85, line=dict(width=0.5, color="white")),
        selector=dict(mode="markers")
    )
    if show_names_s:
        fig_sc.update_traces(
            textposition="top center",
            textfont=dict(size=8, color="white"),
            selector=dict(mode="markers+text")
        )
    fig_sc.update_layout(
        height=530,
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        coloraxis_showscale=True,
        coloraxis_colorbar=dict(title=conc_metric.replace("_share", "") + " %"),
        xaxis=dict(gridcolor="#333"),
        yaxis=dict(gridcolor="#333"),
    )
    st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown(f"""<div class="insight-card">
        <h4>📊 Statistical result</h4>
        <p>
        Pearson r = <strong style="color:#1DB954">{r_f2:.3f}</strong> →
        <strong>{strength_f2} {direction_f2} correlation</strong> between
        streaming concentration and tour intensity.
        R² = <strong style="color:#1DB954">{r2_f2:.1%}</strong>,
        p = {p_f2:.4f} →
        <strong>{"statistically significant " if p_f2 < 0.05 else "not significant "}</strong>.
        </p>
    </div>
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>
        {
    f"Artists with <strong>lower streaming concentration</strong> (streams are distributed more broadly) tour more intensively — consistent with the hypothesis that a deep catalog audience supports touring."
    if r_f2 < -0.2 and p_f2 < 0.05 else
    f"Artists with <strong>higher streaming concentration</strong> tour more intensively — this could mean that a viral hit also drives higher live demand."
    if r_f2 > 0.2 and p_f2 < 0.05 else
    "Streaming concentration is barely related to tour intensity. The two dimensions are largely independent — neither catalog depth nor hit concentration is a reliable predictor of touring activity."
    }
        <br><br>
        <strong>In the context of the overall project:</strong>
        Combined with F1 (listeners → tour scale), this result shows whether the
        <em>quality</em> of streaming activity (broad vs. concentrated) has a different
        predictive power than the <em>quantity</em> (total listeners).
        </p>
    </div>""", unsafe_allow_html=True)
else:
    st.warning("Too few data points after filtering.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F2 — GRAPH 2: Boxplot — Events/year by concentration category
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📦 Graph 2 — Tour intensity by concentration category (box plot)</div>',
            unsafe_allow_html=True
            )
st.markdown("""Artists are grouped into **concentration categories** — from "broad repertoire"
(many tracks contribute to streaming) to "highly concentrated" (a few tracks dominate).
The **box plot** shows the distribution of tour intensity by category and makes
structural differences visible that may be hidden in the scatterplot.""")

bx1, bx2 = st.columns([1, 3])
with bx1:
    n_cats = st.select_slider("Number of categories", [3, 4, 5], value=4, key="f2b_nc")
    bx_metric = st.radio("Y-axis", ["Events last year", "Total events"], key="f2b_ym")

df2b = df2.dropna(subset=["top5_share", "events_last_year", "total_events"]).copy()
y_col_bx = "events_last_year" if bx_metric == "Events last year" else "total_events"

try:
    cat_labels = {
        3: ["🟢 Broad\nrepertoire", "🟡 Moderately\nconcentrated", "🔴 Highly\nconcentrated"],
        4: ["🟢 Broad", "🟡 Moderate", "🟠 Focused", "🔴 Concentrated"],
        5: ["🟢 Very broad", "🟢 Broad", "🟡 Moderate", "🟠 Focused", "🔴 Concentrated"],
    }[n_cats]

    df2b["cat"] = pd.qcut(
        df2b["top5_share"], q=n_cats,
        labels=cat_labels, duplicates="drop"
    )

    bx_colors = ["#1DB954", "#7fb3d3", "#f0c040", "#e05050",
                 "#cc3030"][:n_cats]

    fig_bx2 = go.Figure()
    for i, cat in enumerate(cat_labels):
        sub = df2b[df2b["cat"] == cat][y_col_bx]
        if len(sub) < 2:
            continue
        fig_bx2.add_trace(go.Box(
            y=sub,
            name=f"{cat}<br><sub>n={len(sub)}</sub>",
            marker_color=bx_colors[i],
            line_color=bx_colors[i],
            fillcolor=hex_rgba(bx_colors[i]),
            boxpoints="outliers",
            marker=dict(size=5, opacity=0.7),
            hovertemplate="Events: %{y}<extra></extra>"
        ))

    # Kruskal-Wallis
    kw_groups = [
        df2b[df2b["cat"] == c][y_col_bx].values
        for c in cat_labels
        if len(df2b[df2b["cat"] == c]) > 1
    ]
    kw_str = ""
    if len(kw_groups) >= 2:
        from scipy.stats import kruskal as kruskal_test

        kw_stat, kw_p = kruskal_test(*kw_groups)
        kw_str = f"Kruskal-Wallis H = {kw_stat:.2f}, p = {kw_p:.4f} → {'significant ' if kw_p < 0.05 else 'not significant '}"

    fig_bx2.update_layout(
        title=f"Tour intensity by concentration category — {bx_metric}",
        yaxis_title=bx_metric,
        template="plotly_dark",
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"), height=430,
        xaxis=dict(gridcolor="#333"),
        yaxis=dict(gridcolor="#333"),
        showlegend=False
    )
    with bx2:
        st.plotly_chart(fig_bx2, use_container_width=True)

    if kw_str:
        st.markdown(f"""<div class="insight-card">
            <h4>📊 Statistical test (Kruskal-Wallis)</h4>
            <p>{kw_str}<br>
            <em>Non-parametric test — robust for skewed event-count distributions.</em></p>
        </div>""", unsafe_allow_html=True)

except Exception as e:
    with bx2:
        st.warning(f"Box plot error: {e}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F2 — GRAPH 3: Top-track concentration profile (example artists)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🎵 Graph 3 — Streaming profile: comparing top artists</div>', unsafe_allow_html=True)
st.markdown("""A **stacked bar chart** shows how the total playcount of selected artists
is distributed across their top tracks. This makes the concentration metric intuitive:
you can immediately see who is a "one-hit wonder" and who builds on a
broader catalog.""")

# Select artists for profile graph — by default the 2 extremes + 2 middle ones
if len(df2) >= 4:
    most_conc = df2.nlargest(2, "top5_share")["artist_name"].tolist()
    least_conc = df2.nsmallest(2, "top5_share")["artist_name"].tolist()
    default_sel = most_conc + least_conc
else:
    default_sel = df2["artist_name"].tolist()[:4]

sel_artists = st.multiselect(
    "Select artists (4–8 recommended)",
    options=sorted(df2["artist_name"].tolist()),
    default=default_sel[:6],
    key="f2p_artists"
)

if sel_artists and os.path.exists("data/raw/lastfm_toptracks.csv"):
    df_tracks_raw = pd.read_csv("data/raw/lastfm_toptracks.csv")
    df_tracks_sel = df_tracks_raw[df_tracks_raw["artist_name"].isin(sel_artists)].copy()
    df_tracks_sel["playcount"] = pd.to_numeric(df_tracks_sel["playcount"], errors="coerce")

    n_top_show = st.slider("Show top N tracks", 3, 10, 5, key="f2p_ntracks")

    fig_profile = go.Figure()
    track_colors = [
        "#1DB954", "#17a844", "#139033", "#0f7828",
        "#0b6022", "#f0c040", "#e08030", "#e05050",
        "#cc3030", "#444"
    ]

    for artist in sel_artists:
        sub = df_tracks_sel[df_tracks_sel["artist_name"] == artist] \
            .sort_values("rank").head(n_top_show)
        total_pc = df_tracks_sel[df_tracks_sel["artist_name"] == artist]["playcount"].sum()
        if total_pc == 0 or len(sub) == 0:
            continue

        for j, (_, row) in enumerate(sub.iterrows()):
            pct = row["playcount"] / total_pc * 100
            fig_profile.add_trace(go.Bar(
                name=row["track_name"] if j == 0 else row["track_name"],
                x=[artist],
                y=[pct],
                marker_color=track_colors[j % len(track_colors)],
                text=f"{pct:.0f}%" if pct > 5 else "",
                textposition="inside",
                hovertemplate=(
                    f"<b>{artist}</b><br>"
                    f"Track: {row['track_name']}<br>"
                    f"Share: {pct:.1f}%<br>"
                    f"Plays: {int(row['playcount']):,}<extra></extra>"
                ),
                showlegend=(artist == sel_artists[0]),
                legendgroup=f"track_{j}",
            ))

    fig_profile.update_layout(
        barmode="stack",
        title=f"Top-{n_top_show} track share of total playcount",
        xaxis_title="Artist",
        yaxis_title="Share of total playcount (%)",
        yaxis=dict(range=[0, 100], gridcolor="#333"),
        template="plotly_dark",
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"), height=430,
        legend=dict(orientation="h", y=-0.2, font=dict(size=10)),
        xaxis=dict(tickangle=-20)
    )
    st.plotly_chart(fig_profile, use_container_width=True)

    # table: concentration + events
    tbl_data = df2[df2["artist_name"].isin(sel_artists)][
        ["artist_name", "top5_share", "top3_share", "top1_share", "events_last_year", "total_events"]
    ].sort_values("top5_share", ascending=False)
    tbl_data.columns = ["Artist", "Top-5 %", "Top-3 %", "Top-1 %", "Events/year", "Total events"]
    st.dataframe(tbl_data.set_index("Artist").style.format({
        "Top-5 %": "{:.1f}",
        "Top-3 %": "{:.1f}",
        "Top-1 %": "{:.1f}",
        "Events/year": "{:.0f}",
        "Total events": "{:.0f}",
    }).background_gradient(cmap="RdYlGn_r", subset=["Top-5 %"])
                 .background_gradient(cmap="YlGn", subset=["Events/year"]),
                 use_container_width=True)
else:
    st.info("No artists selected or `lastfm_toptracks.csv` is missing.")

# Summary F2 
st.divider()
st.markdown('<div class="section-title">Summary — Research Question 2</div>', unsafe_allow_html=True)

if len(df2f) >= 5:
    st.markdown(f"""
    | Metric | Value |
    |--------|------|
    | Artists with complete F2 data | {n_f2} ({pct_cov_f2:.0f}%) |
    | Concentration metric | Top-5 track share of total playcount |
    | Tour intensity | Events in the last year (Ticketmaster) |
    | Pearson r | {r_f2:.3f} |
    | R² | {r2_f2:.1%} |
    | p-value | {p_f2:.4f} |
    | Significant | {'Yes ' if p_f2 < 0.05 else 'No '} |
    """)

    st.markdown(f"""<div class="insight-card">
        <h4>🎯 Answer to Research Question 2</h4>
        <p>
        Streaming concentration (top-5 share) shows a
        <strong>{strength_f2} {direction_f2} correlation</strong>
        (r = {r_f2:.3f}, R² = {r2_f2:.1%}) with tour intensity.
        {
    "This supports the hypothesis: artists with a broad and evenly distributed streaming profile tour more intensively — their audience is more loyal and follows them on tour." if r_f2 < -0.2 and p_f2 < 0.05 else
    "Surprisingly, higher concentration is associated with more events — one possible explanation is that a viral hit also increases short-term live demand." if r_f2 > 0.2 and p_f2 < 0.05 else
    "The concentration of streaming activity is not a significant predictor of tour intensity. The nature of popularity (broad vs. concentrated) does not play a decisive role for physical touring activity."
    }
        <br><br>
        <strong>In the overall context:</strong> Compared with F1 (listeners → events: quantitative
        size of popularity), F2 shows that the <em>structure</em> of streaming activity
        {"provides additional predictive power." if p_f2 < 0.05 else "does not provide additional explanatory value."}
        </p>
    </div>""", unsafe_allow_html=True)

st.markdown("""<div class="methodology-note">
    <p>
    <strong>Methodological note:</strong>
    Streaming concentration = share of the top 5 tracks in the total playcount
    of the top 20 tracks returned by Last.fm (<code>artist.getTopTracks</code>).
    This metric slightly underestimates concentration if an artist has more than 20
    relevant tracks. Tour intensity = number of Ticketmaster events in the last
    12 months (reference date: March 2026). Additionally, the Herfindahl-Hirschman Index (HHI)
    was calculated as a stricter concentration measure (available in Graph 1 via the metric selection).
    </p>
</div>""", unsafe_allow_html=True)

st.markdown('<div id="frage-3"></div>', unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════
# RESEARCH QUESTION 3 — Chart Artists vs. Non-Chart Artists
# ══════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown("""<div class="rq-box">
    <h3>🔬 Research Question 3</h3>
    <p>How do current Last.fm listener counts differ between artists who appeared
    in Spotify Weekly Charts (Feb&nbsp;2023–Feb&nbsp;2026) and those who did not?</p>
</div>""", unsafe_allow_html=True)

st.markdown("""**Why this question?**
Spotify charts and Last.fm listeners are two independent popularity signals
from different platforms. If chart artists systematically have more Last.fm listeners,
this points to **cross-platform popularity** — digital popularity is coherent across platforms.
If not, the platforms reflect different user ecosystems.

**Hypothesis:** Artists who appeared in the global Spotify Weekly Chart have significantly
more Last.fm listeners — because both metrics measure general popularity.

**Test method:** Mann-Whitney U (non-parametric, robust against the
strongly right-skewed listener distributions).""")


# F3 load data
@st.cache_data
def load_f3_data():
    p = "data/processed/spotify_charts/chart_artists.csv"
    if not os.path.exists(p):
        return None
    return pd.read_csv(p)


charts_df = load_f3_data()

if charts_df is None:
    st.error("  `data/processed/spotify_charts/chart_artists.csv` is missing.")
    st.code("python scripts/process_spotify_charts.py", language="bash")
    st.stop()

# Join: was_on_chart
charts_df["artist_norm"] = charts_df["artist"].str.lower().str.strip()
df3 = df.copy()
df3["artist_norm"] = df3["artist_name"].str.lower().str.strip()
df3["was_on_chart"] = df3["artist_norm"].isin(set(charts_df["artist_norm"]))

# join Chart-Metrics
chart_merge_cols = [c for c in ["artist_norm", "total_chart_streams", "chart_weeks",
                                "peak_position", "first_chart_date", "last_chart_date"]
                    if c in charts_df.columns]
df3 = df3.merge(charts_df[chart_merge_cols], on="artist_norm", how="left")

for c in ["total_chart_streams", "chart_weeks", "peak_position"]:
    if c in df3.columns:
        df3[c] = pd.to_numeric(df3[c], errors="coerce")

n_chart = int(df3["was_on_chart"].sum())
n_non_chart = int((~df3["was_on_chart"]).sum())
mean_c = df3[df3["was_on_chart"]]["listeners"].mean()
mean_nc = df3[~df3["was_on_chart"]]["listeners"].mean()
ratio = mean_c / mean_nc if mean_nc and mean_nc > 0 else 0

grp_c = df3[df3["was_on_chart"]]["listeners"].dropna()
grp_nc = df3[~df3["was_on_chart"]]["listeners"].dropna()

u_stat = u_p = None
if len(grp_c) >= 5 and len(grp_nc) >= 5:
    u_stat, u_p = stats.mannwhitneyu(grp_c, grp_nc, alternative="two-sided")

# KPIs
st.divider()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Chart artists", n_chart, delta=f"{n_chart / (n_chart + n_non_chart) * 100:.0f}% of dataset")
k2.metric("Non-chart artists", n_non_chart)
k3.metric("Ø listeners chart", f"{mean_c:,.0f}")
k4.metric("Ø listeners non-chart", f"{mean_nc:,.0f}")
k5.metric("Ratio", f"{ratio:.1f}×",
          delta="Chart higher" if ratio > 1 else "no difference",
          delta_color="normal" if ratio > 1 else "off")
st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F3 — GRAPH 1: Box / Violin Plot — listeners by chart status
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📦 Graph 1 — Listener distribution: chart vs. non-chart</div>', unsafe_allow_html=True)
st.markdown("""The **box plot** shows the median, quartiles, and outliers for both groups in direct comparison.""")

g1, g2 = st.columns([1, 3])
with g1:
    show_pts = st.checkbox("Show points", value=True, key="f3_pts")

df3_plot = df3.copy()
df3_plot["Gruppe"] = df3_plot["was_on_chart"].map(
    {True: "✅ In Spotify Chart", False: "❌ Not in Chart"}
)
df3_plot["listeners_plot"] = df3_plot["listeners"]
grp_order = ["❌ Not in Chart", "✅ In Spotify Chart"]

COLORS_F3 = {
    "✅ In Spotify Chart": ("#6366f1", "rgba(99,102,241,0.2)"),
    "❌ Not in Chart": ("#94a3b8", "rgba(148,163,184,0.15)"),
}
pts_mode = "all" if show_pts else "outliers"

fig_f3g1 = go.Figure()
for grp in grp_order:
    sub_d = df3_plot[df3_plot["Gruppe"] == grp]
    col, fill = COLORS_F3[grp]
    fig_f3g1.add_trace(go.Box(
        x=sub_d["listeners_plot"], name=grp,
        orientation="h",
        marker_color=col,
        fillcolor=fill,
        line=dict(color=col, width=1.5),
        boxpoints=pts_mode,
        jitter=0.3,
        pointpos=0,
        marker=dict(size=5, opacity=0.5),
        customdata=sub_d[["artist_name", "listeners"]].values,
        hovertemplate="<b>%{customdata[0]}</b><br>Listeners: %{customdata[1]:,.0f}<extra></extra>",
    ))

fig_f3g1.update_layout(
    title="Last.fm listeners — chart vs. non-chart artists",
    xaxis_title="Last.fm listeners",
    template="plotly_dark",
    paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
    font=dict(color="white"), height=380,
    xaxis=dict(gridcolor="#232840"),
    yaxis=dict(gridcolor="#232840"),
    legend=dict(orientation="h", y=-0.2),
    boxmode="group",
)
with g2:
    st.plotly_chart(fig_f3g1, use_container_width=True)

if u_p is not None:
    log_c2 = np.log10(grp_c + 1)
    log_nc2 = np.log10(grp_nc + 1)
    t_stat2, t_p2 = stats.ttest_ind(log_c2, log_nc2, equal_var=False)
    pooled_std2 = np.sqrt((log_c2.std() ** 2 + log_nc2.std() ** 2) / 2)
    cohens_d2 = (log_c2.mean() - log_nc2.mean()) / pooled_std2 if pooled_std2 > 0 else 0
    eff_lbl2 = ("large" if abs(cohens_d2) >= 0.8 else
                "medium" if abs(cohens_d2) >= 0.5 else
                "small" if abs(cohens_d2) >= 0.2 else "negligible")

    st.markdown(f"""<div class="insight-card">
        <h4>📊 Statistical tests</h4>
        <p>
        <strong>Mann-Whitney U</strong> = {u_stat:.0f} &nbsp;|&nbsp;
        p = <strong style="color:#818cf8">{u_p:.4f}</strong> &nbsp;→&nbsp;
        <strong>{"Significant " if u_p < 0.05 else "Not significant "}</strong>
        <br>
        Welch's t-test (log): t = {t_stat2:.3f} &nbsp;|&nbsp; p = {t_p2:.4f}
        <br>
        Cohen's d = {cohens_d2:.3f} → <strong>{eff_lbl2} effect size</strong>
        <br><br>
        Chart artists have on average <strong style="color:#6366f1">{ratio:.1f}×</strong> more Last.fm listeners.
        {
    " The popularity levels are consistent across platforms — artists who chart on Spotify also have a larger audience on Last.fm." if u_p < 0.05 and ratio > 1
    else " There is no significant difference — Spotify charts and Last.fm listeners partly reflect different user ecosystems."
    }
        </p>
    </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F3 — GRAPH 2: Histogram overlay — listener distribution of both groups
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 2 — Listener distribution (overlay)</div>', unsafe_allow_html=True)
st.markdown("""Overlay histogram of both groups on a log scale.
The shift of the chart distribution to the right visualizes the listener advantage.""")

h1, h2 = st.columns([1, 3])
with h1:
    n_bins_f3 = st.slider("Bins", 15, 60, 30, key="f3_bins")
    norm_hist = st.checkbox("Normalized (density)", value=True, key="f3_norm")

hist_mode = "probability density" if norm_hist else ""

fig_f3g2 = go.Figure()
for grp, col in [("❌ Not in Chart", "#94a3b8"), ("✅ In Spotify Chart", "#6366f1")]:
    sub = df3_plot[df3_plot["Gruppe"] == grp]["listeners_plot"].dropna()
    fig_f3g2.add_trace(go.Histogram(
        x=sub, name=grp,
        histnorm=hist_mode,
        nbinsx=n_bins_f3,
        marker_color=col,
        opacity=0.65,
        hovertemplate=f"{grp}<br>%{{x:.2f}}<br>%{{y:.4f}}<extra></extra>",
    ))

fig_f3g2.update_layout(
    barmode="overlay",
    title="Listener distribution — chart vs. non-chart",
    xaxis_title="Last.fm listeners",
    yaxis_title="Density" if norm_hist else "Number of artists",
    template="plotly_dark",
    paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
    font=dict(color="white"), height=380,
    xaxis=dict(gridcolor="#232840"),
    yaxis=dict(gridcolor="#232840"),
    legend=dict(orientation="h", y=-0.2),
)
with h2:
    st.plotly_chart(fig_f3g2, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F3 — GRAPH 3: Scatterplot chart_weeks vs. listeners
# ══════════════════════════════════════════════════════════════════════════
if "chart_weeks" in df3.columns and df3["chart_weeks"].notna().sum() >= 5:
    st.markdown('<div class="section-title">📈 Graph 3 — Chart intensity vs. Last.fm listeners</div>',
                unsafe_allow_html=True)
    st.markdown("Chart artists only. The longer an artist stayed in the Spotify chart, the more Last.fm listeners they have? " +
                tt("OLS", "OLS trend line") + " shows the relationship.", unsafe_allow_html=True)

    s1, s2 = st.columns([1, 3])
    with s1:
        x_metric_f3 = st.radio("X-axis",
                               ["chart_weeks", "total_chart_streams"],
                               index=0, key="f3_x",
                               format_func=lambda x: {"chart_weeks": "Weeks in chart",
                                                      "total_chart_streams": "Total streams"}[x])
        log_y_f3 = st.checkbox("Log Y", value=True, key="f3_logy")
        lbl_f3 = st.checkbox("Names", value=False, key="f3_lbl")

    df_sc3 = df3.dropna(subset=[x_metric_f3, "listeners"]).copy()
    df_sc3 = df_sc3[df_sc3["was_on_chart"]]
    df_sc3["x_plot"] = np.log10(df_sc3[x_metric_f3] + 1)
    df_sc3["y_plot"] = np.log10(df_sc3["listeners"] + 1) if log_y_f3 else df_sc3["listeners"]

    if len(df_sc3) >= 5:
        r_f3, p_f3 = stats.pearsonr(df_sc3["x_plot"], df_sc3["y_plot"])
        coef_f3 = np.polyfit(df_sc3["x_plot"], df_sc3["y_plot"], 1)
        x_line_f3 = np.linspace(df_sc3["x_plot"].min(), df_sc3["x_plot"].max(), 200)
        y_line_f3 = np.polyval(coef_f3, x_line_f3)

        r2_f3 = r_f3 ** 2
        m1f3, m2f3, m3f3 = st.columns(3)
        m1f3.metric("n chart artists", len(df_sc3))
        m2f3.metric("Pearson r", f"{r_f3:.3f}")
        m3f3.metric("p-value", f"{p_f3:.4f}",
                    delta="significant " if p_f3 < 0.05 else "not significant ",
                    delta_color="normal" if p_f3 < 0.05 else "inverse")

        fig_f3g3 = px.scatter(
            df_sc3, x="x_plot", y="y_plot",
            hover_name="artist_name",
            hover_data={"x_plot": False, "y_plot": False,
                        "listeners": ":,", x_metric_f3: True},
            color="listeners",
            color_continuous_scale="Viridis",
            text="artist_name" if lbl_f3 else None,
            labels={
                "x_plot": f"log₁₀({x_metric_f3.replace('_', ' ').title()})",
                "y_plot": "log₁₀(Last.fm listeners)" if log_y_f3 else "Last.fm listeners",
            },
            title=f"Chart intensity vs. listeners  |  r = {r_f3:.3f}  |  n = {len(df_sc3)}",
            template="plotly_dark",
        )
        fig_f3g3.add_trace(go.Scatter(
            x=x_line_f3, y=y_line_f3, mode="lines", name="OLS",
            line=dict(color="#f59e0b", width=2.5), hoverinfo="skip",
        ))
        fig_f3g3.update_traces(
            marker=dict(size=9, opacity=0.85, line=dict(width=0.5, color="white")),
            selector=dict(mode="markers")
        )
        if lbl_f3:
            fig_f3g3.update_traces(
                textposition="top center", textfont=dict(size=8, color="white"),
                selector=dict(mode="markers+text")
            )
        fig_f3g3.update_layout(
            height=480, paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#232840"), yaxis=dict(gridcolor="#232840"),
            coloraxis_showscale=False,
        )
        with s2:
            st.plotly_chart(fig_f3g3, use_container_width=True)

    st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F3 — Summary
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Summary — Research Question 3</div>', unsafe_allow_html=True)

st.markdown(f"""| Metric | Value |
|--------|------|
| Chart artists (Feb 2023–Feb 2026) | {n_chart} ({n_chart / (n_chart + n_non_chart) * 100:.0f}%) |
| Non-chart artists | {n_non_chart} |
| Ø listeners chart artists | {mean_c:,.0f} |
| Ø listeners non-chart artists | {mean_nc:,.0f} |
| Ratio | {ratio:.1f}× |
| Mann-Whitney U p-value | {f"{u_p:.4f}" if u_p is not None else "n/a"} |
| Significant (α=0.05) | {"Yes " if u_p is not None and u_p < 0.05 else "No "} |""")

if u_p is not None:
    st.markdown(f"""<div class="insight-card">
        <h4>🎯 Answer to Research Question 3</h4>
        <p>
        Artists who appeared in the global Spotify Weekly Chart between Feb 2023 and Feb 2026
        have on average <strong style="color:#818cf8">{ratio:.1f}×</strong> more Last.fm listeners
        ({mean_c:,.0f} vs. {mean_nc:,.0f}).
        <br><br>
        The difference is <strong>{"statistically significant " if u_p < 0.05 else "not statistically significant "}</strong>
        (Mann-Whitney U, p = {u_p:.4f}).
        {
    " This supports the hypothesis: digital popularity is coherent across platforms — Spotify chart success and Last.fm audience size reflect the same construct from different angles." if u_p < 0.05
    else " This rejects the hypothesis: Spotify charts and Last.fm listeners reflect different fan bases — the platform ecosystems are only weakly connected."
    }
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""<div class="methodology-note">
    <p>
    Chart assignment is based on normalization of artist names (lowercase, trimmed).
    In collaborations, each participating artist is counted separately.
    Period: February 1, 2023 – February 28, 2026 (global Spotify Weekly Charts).
    Last.fm listener counts: March 2026 snapshot (current at the time of data collection).
    Mann-Whitney U is preferred over the t-test because listener distributions are strongly right-skewed.
    </p>
</div>
""", unsafe_allow_html=True)