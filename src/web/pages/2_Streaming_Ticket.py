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
st.markdown(
    '<a id="frage-1" style="display:block; position:relative; top:-80px;"></a>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="rq-box" style="margin-top: 28px;">
    <h3>🔬 Research Question 1</h3>
    <p>How does the number of Last.fm listeners correlate with the scale of an artist's tour,
    measured by the number of events scheduled?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**What are we measuring?**
We examine whether artists with more Last.fm listeners also tend to have larger tours. Digital popularity is measured using the current number of Last.fm listeners. Tour scale is measured as the total number of Ticketmaster events found for each artist between 2022 and 2026.
**Why is this relevant?**
If digital reach is associated with more live events, this suggests that online popularity may be a useful indicator of real-world live demand.
""")

st.divider()

# ══════════════════════════════════════════════════════
# GRAPH 1 — Scatterplot
# ══════════════════════════════════════════════════════
st.markdown(
'<div class="section-title">📈 Graph 1 — Scatterplot: Last.fm listeners vs. number of events</div>',
unsafe_allow_html=True
)

st.markdown("""
Each point represents one artist. The x-axis shows the number of Last.fm listeners, and the y-axis shows the total number of Ticketmaster events. The green trend line summarizes the overall direction of the relationship: if the line rises, artists with more listeners tend to have more events on average; if it stays flat, there is little to no linear relationship.
The filters allow users to exclude outliers or focus on specific genres to see whether the pattern remains stable.
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
    show_labels = st.checkbox("Show names", value=False, key="g1_lbl")

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
    abs_r = abs(r)

    if abs_r < 0.1:
        relationship_label = "No meaningful relationship"
        relationship_text = "no meaningful linear relationship"
    elif abs_r < 0.3:
        relationship_label = "Weak"
        relationship_text = f"a weak {'positive' if r > 0 else 'negative'} relationship"
    elif abs_r < 0.5:
        relationship_label = "Moderate"
        relationship_text = f"a moderate {'positive' if r > 0 else 'negative'} relationship"
    else:
        relationship_label = "Strong"
        relationship_text = f"a strong {'positive' if r > 0 else 'negative'} relationship"

    significance_label = "Yes" if p < 0.05 else "No"

    m1, = st.columns(1)
    m1.metric("n artists", len(df1))


    # Plot
    hover = {"listeners": ":,", "total_events": True}
    if "tags" in df1.columns:
        hover["tags"] = True

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
        title=f"Last.fm listeners vs. tour scale",
        template="plotly_dark"
    )
    fig1.add_trace(go.Scatter(
        x=_x1, y=_y1, mode="lines", name="trend line",
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
        paper_bgcolor="#0e0e0e",
        plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#333", tickformat=","),
        yaxis=dict(gridcolor="#333")
    )
    st.plotly_chart(fig1, use_container_width=True)



    # Interpretation
    if abs_r < 0.1:
        interp_text = (
        "The trend line is nearly flat. Artists with more Last.fm listeners do not systematically play more concerts. "
        "Streaming popularity alone is not a strong predictor of tour scale: some artists with relatively few listeners "
        "tour extensively, while some of the most-streamed artists play only a handful of shows."
        )
    elif p < 0.05 and r > 0:
        interp_text = (
        "The trend line rises from left to right. Artists with more Last.fm listeners tend to play more concerts. "
        "This suggests that streaming popularity and tour scale move in the same direction, "
        "though the wide spread of points shows that many other factors also shape how extensively an artist tours."
        )
    elif p < 0.05 and r < 0:
        interp_text = (
        "The trend line falls from left to right. Artists with more Last.fm listeners tend to play fewer concerts. "
        "This might reflect that highly streamed artists are more selective about their live appearances, "
        "or that smaller artists rely more heavily on touring to build their audience."
        )
    else:
        interp_text = (
        "The trend line shows a slight tendency, but the overall pattern is not strong enough to draw a firm conclusion. "
        "The data points are spread widely, suggesting that factors beyond streaming popularity — "
        "such as genre, career stage, or management strategy — play an equally important role in tour scale."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>
        {interp_text}
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("Too few data points after filtering. Please adjust the filters.")

st.divider()
# ══════════════════════════════════════════════════════
# GRAPH 2 — Bar Chart (Grouped listener bins)
# ══════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">📊 Graph 2 — Average events per listener group</div>',
    unsafe_allow_html=True
)

# Dynamic explanation text (will update with controls)
explanation_placeholder = st.empty()


qa, qb = st.columns([1, 3])
with qa:
    n_groups = st.select_slider(
        "Number of groups",
        options=[3, 4, 5, 6, 8, 10],
        value=4,
        key="g2_ng"
    )
    agg = st.radio("Y-axis", ["Mean of events", "Median of events"], index=0, key="g2_agg")

    group_share = 100 / n_groups

explanation_placeholder.markdown(f"""
Artists are sorted by their Last.fm listener count and then divided into <strong>{n_groups} equally sized groups</strong>. 
This means that each group contains about <strong>{group_share:.1f}%</strong> of all artists in the dataset. 
G1 represents the artists with the fewest listeners, while G{n_groups} represents those with the most listeners. 
For each group, the chart shows the <strong>{agg.lower()}</strong> number of events, making broad patterns easier to compare than in the scatterplot alone.
""", unsafe_allow_html=True)

try:
    df2 = df.copy()
    labels = [f"G{i + 1}" for i in range(n_groups)]
    df2["group"] = pd.qcut(df2["listeners"], q=n_groups, labels=labels, duplicates="drop")
    agg_fn = "mean" if "Mean" in agg else "median"

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
        title=f"{agg} number of events per listener group  ({n_groups} groups, G1 = fewest listeners)",
        xaxis_title="Listener group",
        yaxis_title=f"{agg} events",
        template="plotly_dark",
        paper_bgcolor="#0e0e0e",
        plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        height=400,
        xaxis=dict(gridcolor="#333"),
        yaxis=dict(gridcolor="#333"),
        showlegend=False
    )

    with qb:
        st.plotly_chart(fig2, use_container_width=True)

    values = grouped["avg_events"].tolist()
    g1_val = values[0]
    gn_val = values[-1]

    monotonic_increasing = all(values[i] <= values[i + 1] for i in range(len(values) - 1))
    monotonic_decreasing = all(values[i] >= values[i + 1] for i in range(len(values) - 1))

    if abs(gn_val - g1_val) < 0.5:
        interp_text = (
            "The grouped values remain very similar across listener groups. "
            "This suggests that artists with more listeners do not systematically have more scheduled events."
        )
    elif monotonic_increasing:
        interp_text = (
            f"The grouped values increase from G1 to G{n_groups}, which suggests that artists with more listeners "
            f"tend to have more scheduled events on average. The pattern is clearer here than in the raw scatterplot, "
            f"although it still remains descriptive rather than causal."
        )
    elif monotonic_decreasing:
        interp_text = (
            f"The grouped values decrease from G1 to G{n_groups}, which suggests that artists with more listeners "
            f"tend to have fewer scheduled events on average. This pattern should be interpreted cautiously and together "
            f"with the scatterplot and correlation analysis."
        )
    else:
        interp_text = (
            "The grouped values do not follow a clear step-by-step pattern from low-listener to high-listener artists. "
            "This suggests that listener count is not strongly associated with tour scale in a consistent way."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>{interp_text}</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.warning(f"Grouping failed: {e}")

st.divider()

# ══════════════════════════════════════════════════════
# GRAPH 3 — Histogram (Distribution)
# ══════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">📉 Graph 3 — Distribution of Last.fm listeners</div>',
    unsafe_allow_html=True
)
st.markdown("""
This histogram shows how Last.fm listener counts are distributed across all artists in the dataset. 
The x-axis represents listener count, and the y-axis shows how many artists fall into each range. 
The dashed and dotted vertical lines mark the median and mean.
""")

ha, hb = st.columns([1, 3])
with ha:
    n_bins = st.slider("Number of bins", 10, 50, 30, key="g3_bins")
    log_x = st.checkbox("Logarithmic X-axis", value=False, key="g3_log")
with hb:
    x_data = np.log10(df["listeners"] + 1) if log_x else df["listeners"]
    x_lab = "log₁₀(Last.fm listeners)" if log_x else "Last.fm listeners"
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(
        x=x_data,
        nbinsx=n_bins,
        name="Artists",
        marker=dict(
            color="#1DB954",
            opacity=0.8,
            line=dict(width=0.5, color="#0e0e0e")
        ),
        hovertemplate="Listeners: %{x}<br>Count: %{y}<extra></extra>"
    ))
    med = float(np.median(x_data))
    avg = float(np.mean(x_data))
    fig3.add_vline(
        x=med,
        line=dict(color="#00d4ff", width=2, dash="dash"),
        annotation_text=f"Median: {10 ** med:,.0f}" if log_x else f"Median: {med:,.0f}",
        annotation_font_color="#00d4ff"
    )
    fig3.add_vline(
        x=avg,
        line=dict(color="#ff8c00", width=2, dash="dot"),
        annotation_text=f"Mean: {10 ** avg:,.0f}" if log_x else f"Mean: {avg:,.0f}",
        annotation_font_color="#ff8c00",
        annotation_position="top left"
    )
    fig3.update_layout(
        title="Distribution of Last.fm listeners across all artists",
        xaxis_title=x_lab,
        yaxis_title="Number of artists",
        template="plotly_dark",
        paper_bgcolor="#0e0e0e",
        plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        height=380,
        xaxis=dict(gridcolor="#333", tickformat=","),
        yaxis=dict(gridcolor="#333"),
        showlegend=False
    )
    st.plotly_chart(fig3, use_container_width=True)

if log_x:
    scale_note = "The logarithmic x-axis spreads out the lower range and compresses the long upper tail, making the shape easier to read."
else:
    scale_note = "The long tail toward the right shows that only a few artists reach very high listener counts."

st.markdown(f"""
<div class="insight-card">
    <h4>🔍 Interpretation</h4>
    <p>
        Most artists in this dataset have relatively modest listener counts, while a small number of highly popular artists 
        stand far above the rest. This uneven distribution is worth keeping in mind when thinking about the relationship 
        between listeners and tour scale: the artists driving any visible correlation are likely a small group at the top, 
        rather than a broad pattern across all artists. {scale_note}
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════
# SUMMARY F1
# ══════════════════════════════════════════════════════
st.markdown('<div class="section-title">Summary — Research Question 1</div>',
    unsafe_allow_html=True)

st.markdown(f"""<div class="insight-card">
    <h4>🎯 Answer to Research Question 1</h4>
    <p>
        The graphs suggest that artists with a larger Last.fm audience tend to schedule more events overall, 
        but this pattern is not uniform across all artists. Most of the dataset consists of artists with 
        mid-range listener counts, while a small number of highly popular artists stand out clearly. 
        Among those top artists, a higher listener count does appear to go hand in hand with a broader 
        tour presence — more dates, more cities, more events. For the majority of artists in the dataset, 
        however, listener count alone does not reliably predict how extensively they tour.
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
    relate to the intensity of their touring, measured by total events?</p>
</div>""", unsafe_allow_html=True)

st.markdown("""
**What are we measuring?**

**Streaming concentration** describes how strongly an artist's total streaming activity is concentrated in only a few top tracks. A high Top-5 share means that a large proportion of all streams comes from only a small number of songs — a lower value means streams are spread more broadly across the catalogue.

**Tour scale** is measured as the total number of Ticketmaster events across all available data.

**Hypothesis:** Artists with a broader streaming profile may tour more extensively because their audience engages with a wider range of their music, which could sustain demand for live performances across a longer period.
""")

f2_required = ["top5_share", "total_events"]
f2_missing = [c for c in f2_required if c not in df.columns]
if f2_missing:
    st.error(f"Missing columns: {f2_missing}")
    st.code("""
# Execution order:
python scripts/collect_toptracks.py    # Fetch Last.fm top tracks
python scripts/join_data.py            # Calculate concentration + join
    """)
    st.stop()

df2 = df.dropna(subset=["top5_share", "total_events"]).copy()
df2["top5_share"] = pd.to_numeric(df2["top5_share"], errors="coerce")
df2["total_events"] = pd.to_numeric(df2["total_events"], errors="coerce")
df2 = df2.dropna(subset=["top5_share", "total_events"])

n_f2 = len(df2)
pct_cov_f2 = n_f2 / len(df) * 100
st.info(f"📊 {n_f2} artists with complete data for this analysis ({pct_cov_f2:.0f}% of the dataset)")

if n_f2 < 10:
    st.warning("Too few data points. Please run `collect_toptracks.py`.")
    st.stop()

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F2 — GRAPH 1: Scatterplot concentration vs. events_last_year
# ══════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">📈 Graph 1 — Does a concentrated streaming profile go hand in hand with more live events?</div>',
    unsafe_allow_html=True
)

st.markdown("""
Each point represents one artist with complete data on both streaming concentration and total touring activity. 
The x-axis shows what share of total playcount comes from an artist's top tracks — a high value means 
the audience focuses heavily on just a few songs, a low value means plays are spread across many tracks. 
The y-axis shows the total number of Ticketmaster events across all available data. 
The green trend line summarizes the overall direction: rising means more concentrated artists tend to 
tour more, falling means broader catalogues go along with more events.
""")

sc1, sc2 = st.columns([2, 1])
with sc1:
    conc_metric = st.radio(
        "Concentration metric (X-axis)",
        ["top5_share", "top3_share", "top1_share"],
        index=0,
        horizontal=True,
        key="f2s_metric"
    )
    metric_labels = {
        "top5_share": "Share of top 5 tracks in total playcount (%)",
        "top3_share": "Share of top 3 tracks in total playcount (%)",
        "top1_share": "Share of track #1 in total playcount (%)",
    }

with sc2:
    log_y_s = st.checkbox("Log Y (events)", value=False, key="f2s_logy")
    show_names_s = st.checkbox("Show names", value=False, key="f2s_names")

sel_genres_f2 = st.multiselect(
    "🎵 Genre filter", options=top_genres, default=[], key="f2s_genres"
)

if conc_metric not in df2.columns:
    st.warning(f"Metric `{conc_metric}` not in dataset — only top5_share is available.")
    conc_metric = "top5_share"

df2f = df2.copy()
df2f = df2f.dropna(subset=[conc_metric, "total_events"])

if sel_genres_f2 and "tags" in df2f.columns:
    df2f = df2f[df2f["tags"].apply(
        lambda x: any(g in extract_genres(x) for g in sel_genres_f2)
    )]

if len(df2f) >= 5:
    x_vals = df2f[conc_metric]
    y_vals = np.log10(df2f["total_events"] + 1) if log_y_s else df2f["total_events"]

    plot_df2 = df2f.copy()
    plot_df2["y_plot"] = y_vals.values

    hover_f2 = {
        conc_metric: ":.1f",
        "total_events": True,
        "listeners": ":,",
    }
    if "tags" in plot_df2.columns:
        hover_f2["tags"] = True

    _c_sc = np.polyfit(plot_df2[conc_metric], plot_df2["y_plot"], 1)
    _x_sc = np.linspace(plot_df2[conc_metric].min(), plot_df2[conc_metric].max(), 200)
    _y_sc = np.polyval(_c_sc, _x_sc)

    slope = _c_sc[0]
    trend_direction = "positive" if slope > 0 else "negative"
    top_n_label = conc_metric.replace("top", "").replace("_share", "")

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
            "y_plot": f"{'log₁₀(' if log_y_s else ''}Total events{')' if log_y_s else ''}",
        },
        title="Streaming concentration vs. total number of Ticketmaster events",
        template="plotly_dark"
    )

    fig_sc.add_trace(go.Scatter(
        x=_x_sc, y=_y_sc, mode="lines", name="Trend line",
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
        paper_bgcolor="#0e0e0e",
        plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        coloraxis_showscale=True,
        coloraxis_colorbar=dict(title=conc_metric.replace("_share", "") + " %"),
        xaxis=dict(gridcolor="#333"),
        yaxis=dict(gridcolor="#333"),
    )

    st.plotly_chart(fig_sc, use_container_width=True)

    if abs(slope) < 2:
        interp_text_f2 = (
            f"The trend line is nearly flat, meaning that the share of plays coming from the "
            f"top {top_n_label} track(s) shows little to no consistent relationship with total "
            f"event count across artists in this dataset. "
            "Streaming concentration alone does not appear to be a meaningful indicator of "
            "how extensively an artist tours."
        )
    elif trend_direction == "negative":
        interp_text_f2 = (
            f"The trend line slopes downward, suggesting that artists with a broader streaming profile — "
            f"where plays are spread across many tracks — tend to have more Ticketmaster events in total. "
            "However, total event count also reflects how long an artist has been active, "
            "so established artists with large catalogues may simply have had more time to accumulate both "
            "a diverse streaming profile and a long touring history."
        )
    else:
        interp_text_f2 = (
            f"The trend line slopes upward, suggesting that artists with a more concentrated streaming profile — "
            f"where a large share of plays comes from just the top {top_n_label} track(s) — tend to have "
            f"more Ticketmaster events in total. "
            "This pattern should be read carefully: total event count grows over an artist's entire career, "
            "so artists who have been active longer naturally accumulate more events regardless of their "
            "streaming profile."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>{interp_text_f2}</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("Too few data points after filtering.")

st.divider()
# ══════════════════════════════════════════════════════════════════════════
# F2 — GRAPH 2: Boxplot — Events/year by concentration category
# ══════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">📦 Graph 2 — Do artists with broader or more concentrated streaming profiles tour more?</div>',
    unsafe_allow_html=True
)

st.markdown("""
Artists are divided into equally sized categories based on how concentrated their streaming activity is — 
from broad profiles where plays are spread across many tracks, to concentrated profiles where a few tracks 
dominate. For each category, the box plot shows the spread of total Ticketmaster events: the line inside 
the box marks the median, the box contains the middle 50% of values, and the whiskers show the typical range. 
Individual points are outliers. The label n shows how many artists are in each category.
""", unsafe_allow_html=True)

bx1, bx2 = st.columns([1, 3])
with bx1:
    n_cats = st.select_slider("Number of categories", [3, 4, 5], value=4, key="f2b_nc")

df2b = df2.dropna(subset=["top5_share", "total_events"]).copy()

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

    bx_colors = ["#1DB954", "#7fb3d3", "#f0c040", "#e05050", "#cc3030"][:n_cats]

    fig_bx2 = go.Figure()
    for i, cat in enumerate(cat_labels):
        sub = df2b[df2b["cat"] == cat]["total_events"]
        if len(sub) < 2:
            continue
        fig_bx2.add_trace(go.Box(
            y=sub,
            name=f"{cat}<br><sub>n = {len(sub)} artists</sub>",
            marker_color=bx_colors[i],
            line_color=bx_colors[i],
            fillcolor=hex_rgba(bx_colors[i]),
            boxpoints="outliers",
            marker=dict(size=5, opacity=0.7),
            hovertemplate="Events: %{y}<extra></extra>"
        ))

    fig_bx2.update_layout(
        title="Total Ticketmaster events by streaming concentration category",
        yaxis_title="Total events",
        template="plotly_dark",
        paper_bgcolor="#0e0e0e",
        plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        height=430,
        xaxis=dict(gridcolor="#333"),
        yaxis=dict(gridcolor="#333"),
        showlegend=False
    )

    with bx2:
        st.plotly_chart(fig_bx2, use_container_width=True)

    # Interpretation based on median pattern only
    medians = (
        df2b.groupby("cat", observed=True)["total_events"]
        .median()
        .reindex(cat_labels)
        .tolist()
    )
    medians_clean = [m for m in medians if m is not None and not pd.isna(m)]

    median_diff = max(medians_clean) - min(medians_clean) if medians_clean else 0
    monotonic_up = all(medians_clean[i] <= medians_clean[i+1] for i in range(len(medians_clean)-1))
    monotonic_down = all(medians_clean[i] >= medians_clean[i+1] for i in range(len(medians_clean)-1))

    if median_diff < 5:
        interp_text_bx = (
            "The median total event counts are very similar across all concentration categories. "
            "This suggests that whether an artist's streams are spread broadly or focused on a few tracks "
            "does not consistently relate to how many live events they have had overall."
        )
    elif monotonic_down:
        interp_text_bx = (
            "The median event count tends to decrease from broader to more concentrated profiles. "
            "Artists whose plays are spread across many tracks appear to have accumulated more "
            "Ticketmaster events in total. This could reflect that a diverse catalogue sustains "
            "audience interest over a longer and more active touring career."
        )
    elif monotonic_up:
        interp_text_bx = (
            "The median event count tends to increase from broader to more concentrated profiles. "
            "Artists with a few dominant tracks appear to have more Ticketmaster events in total on average. "
            "One possible explanation is that breakout tracks create stronger and more sustained demand "
            "for live performances over time."
        )
    else:
        interp_text_bx = (
            "The median event counts vary across the concentration categories, but without a clear "
            "step-by-step pattern from broad to concentrated. This suggests that streaming concentration "
            "alone does not reliably predict how extensively an artist has toured."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>{interp_text_bx}</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    with bx2:
        st.warning(f"Box plot error: {e}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F2 — GRAPH 3: Top-track concentration profile (example artists)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🎵 Explore individual artist streaming profiles</div>', unsafe_allow_html=True)
st.markdown("""
Select any artists below to compare how their total playcount is distributed across their top tracks. 
Artists on the left side of the chart spread their plays across many songs — those on the right are dominated by just a few. 
Use the controls to explore different combinations and see who relies on a broad catalogue versus a handful of hits.
""")

if len(df2) >= 4:
    most_conc = df2.nlargest(2, "top5_share")["artist_name"].tolist()
    least_conc = df2.nsmallest(2, "top5_share")["artist_name"].tolist()
    default_sel = most_conc + least_conc
else:
    default_sel = df2["artist_name"].tolist()[:4]

sel_artists = st.multiselect(
    "Select artists to compare (4–8 recommended)",
    options=sorted(df2["artist_name"].tolist()),
    default=default_sel[:6],
    key="f2p_artists"
)

if sel_artists and os.path.exists("data/raw/lastfm_toptracks.csv"):
    df_tracks_raw = pd.read_csv("data/raw/lastfm_toptracks.csv")
    df_tracks_sel = df_tracks_raw[df_tracks_raw["artist_name"].isin(sel_artists)].copy()
    df_tracks_sel["playcount"] = pd.to_numeric(df_tracks_sel["playcount"], errors="coerce")

    n_top_show = st.slider("Show top N tracks per artist", 3, 10, 5, key="f2p_ntracks")

    # Purple-toned color palette for tracks
    track_colors = [
        "#c084fc",  # Track 1 — light purple
        "#a855f7",  # Track 2
        "#9333ea",  # Track 3
        "#7c3aed",  # Track 4
        "#6d28d9",  # Track 5
        "#5b21b6",  # Track 6
        "#4c1d95",  # Track 7
        "#3b0764",  # Track 8
        "#2e1065",  # Track 9
        "#1e0a4a",  # Track 10
    ]

    fig_profile = go.Figure()

    for artist in sel_artists:
        sub = df_tracks_sel[df_tracks_sel["artist_name"] == artist] \
            .sort_values("playcount", ascending=False).head(n_top_show)
        total_pc = df_tracks_sel[df_tracks_sel["artist_name"] == artist]["playcount"].sum()
        if total_pc == 0 or len(sub) == 0:
            continue

        for j, (_, row) in enumerate(sub.iterrows()):
            pct = row["playcount"] / total_pc * 100
            fig_profile.add_trace(go.Bar(
                name=f"Track {j+1}",
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
        title=f"Share of total playcount by top {n_top_show} tracks",
        xaxis_title="Artist",
        yaxis_title="Share of total playcount (%)",
        yaxis=dict(range=[0, 100], gridcolor="#333"),
        template="plotly_dark",
        paper_bgcolor="#0e0e0e",
        plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        height=450,
        legend=dict(
            title=dict(text="Track rank", font=dict(size=11, color="white")),
            orientation="v",
            x=1.02,
            y=1,
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(tickangle=-20, gridcolor="#333"),
        margin=dict(r=120)
    )

    st.plotly_chart(fig_profile, use_container_width=True)

    # Table
    tbl_data = df2[df2["artist_name"].isin(sel_artists)][
        ["artist_name", "top5_share", "top3_share", "top1_share", "total_events"]
    ].sort_values("top5_share", ascending=False).copy()
    tbl_data.columns = ["Artist", "Top-5 share %", "Top-3 share %", "Top-1 share %", "Total events"]

st.markdown('<div class="section-title">📋 Concentration & touring overview</div>', unsafe_allow_html=True)

st.dataframe(
    tbl_data.set_index("Artist").style
    .format({
        "Top-5 share %": "{:.1f}",
        "Top-3 share %": "{:.1f}",
        "Top-1 share %": "{:.1f}",
        "Total events": "{:.0f}",
    })
    .background_gradient(cmap="Purples", subset=["Top-5 share %", "Top-3 share %", "Top-1 share %"])
    .background_gradient(cmap="YlGn", subset=["Total events"])
    .set_properties(**{
        "font-size": "13px",
        "text-align": "center",
        "color": "white",
        "background-color": "#1a1a1a",
    })
    .set_table_styles([{
        "selector": "th",
        "props": [
            ("font-size", "13px"),
            ("text-align", "center"),
            ("padding", "6px 12px"),
            ("color", "white"),
            ("background-color", "#2a2a2a"),
        ]
    }]),
    use_container_width=True
)

# ══════════════════════════════════════════════════════════════════════════
# F2 — Summary
# ══════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div class="section-title">Summary — Research Question 2</div>', unsafe_allow_html=True)

# Derive answer from trendline slope computed in Graph 1
if len(df2f) >= 5:
    if abs(slope) < 2:
        answer_f2 = (
            "Across the artists in this dataset, the concentration of streaming activity — whether plays "
            "are focused on a few tracks or spread broadly — does not appear to consistently relate to "
            "how many live events an artist has. Artists with very different streaming profiles show "
            "similar levels of touring activity overall."
        )
        context_f2 = (
            "This suggests that the structure of an artist's streaming catalogue is not a strong indicator "
            "of tour scale. Other factors, such as overall audience size or genre, may play a larger role."
        )
    elif slope < 0:
        answer_f2 = (
            "Artists with a broader streaming profile — where plays are distributed more evenly across "
            "many tracks — tend to have more Ticketmaster events in total. This pattern suggests that "
            "a diverse catalogue may support a more sustained and extensive touring career."
        )
        context_f2 = (
            "Compared to overall listener count, the structure of streaming activity adds a different "
            "perspective: it is not just how many people listen, but how broadly they engage with an "
            "artist's catalogue that may relate to touring scale."
        )
    else:
        answer_f2 = (
            "Artists with a more concentrated streaming profile — where a large share of plays comes "
            "from just a few tracks — tend to have more Ticketmaster events in total. This could reflect "
            "that having one or a few standout tracks creates stronger and more sustained demand for "
            "live performances."
        )
        context_f2 = (
            "This finding contrasts with the idea that only broadly popular artists tour extensively. "
            "Even artists known primarily for a handful of hits appear to maintain an active live presence."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>🎯 Answer to Research Question 2</h4>
        <p>{answer_f2}</p>
        <br>
        <p><strong>Broader context:</strong> {context_f2}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="methodology-note">
        <p>
        <strong>Methodological note:</strong> Streaming concentration is measured as the share of the 
        top 5 tracks in the total playcount of the top 20 tracks returned by Last.fm 
        (<code>artist.getTopTracks</code>). Tour scale is measured as total Ticketmaster events across 
        all available data (no date filter applied). Artists without complete data on both dimensions 
        were excluded from Graphs 1 and 2.
        </p>
    </div>
    """, unsafe_allow_html=True)

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
strongly right-skewed listener distributions). 

**Spotify Weekly Charts** are weekly rankings of the most-streamed songs on Spotify. In our analysis, an artist is classified as a “Chart Artist” if they appeared at least once in the global Spotify Weekly Charts between February 2023 and February 2026. Rather than using every weekly chart, we sampled one representative chart week per month to retain broad coverage over time while keeping the dataset manageable.""")


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



# ══════════════════════════════════════════════════════════════════════════
# F3 — GRAPH 1: Box Plot — listeners by chart status
# ══════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">📦 Graph 1 — Listener distribution: Chart vs. Non-Chart</div>',
    unsafe_allow_html=True
)

st.markdown("""
This box plot compares the distribution of Last.fm listener counts between Chart Artists and Non-Chart Artists.
The line inside each box marks the median, the box contains the middle 50% of values, and the points show individual artists or outliers.
This allows us to compare not only central tendency, but also the spread and overlap of listener counts across the two groups.            
""")

# KPIs
st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Chart artists", n_chart, delta=f"{n_chart / (n_chart + n_non_chart) * 100:.0f}% of dataset")
k2.metric("Non-chart artists", n_non_chart)
k3.metric("Ø listeners chart", f"{mean_c:,.0f}")
k4.metric("Ø listeners non-chart", f"{mean_nc:,.0f}")
k5.metric("Ratio", f"{ratio:.1f}×",
          delta="Chart higher" if ratio > 1 else "no difference",
          delta_color="normal" if ratio > 1 else "off")
st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

g1, g2 = st.columns([1, 3])
with g1:
    show_pts = st.checkbox("Show points", value=True, key="f3_pts")

    st.markdown("")
    st.markdown("**Color legend**")

    st.markdown(
        """
        <div style="display:flex; align-items:center; margin-bottom:8px;">
            <span style="display:inline-block; width:14px; height:14px; background:#24f803; border-radius:3px; margin-right:8px;"></span>
            <span>In Spotify Chart ✅</span>
        </div>
        <div style="display:flex; align-items:center;">
            <span style="display:inline-block; width:14px; height:14px; background:#fa0303; border-radius:3px; margin-right:8px;"></span>
            <span>Not in Chart ❌</span>
        </div>
        """,
        unsafe_allow_html=True
    )

df3_plot = df3.copy()
df3_plot["Gruppe"] = df3_plot["was_on_chart"].map(
    {True: "In Spotify Chart ✅", False: "Not in Chart ❌"}
)
df3_plot["listeners_plot"] = df3_plot["listeners"]
grp_order = ["Not in Chart ❌", "In Spotify Chart ✅"]

COLORS_F3 = {
    "In Spotify Chart ✅": ("#24f803", "rgba(99,102,241,0.2)"),
    "Not in Chart ❌": ("#fa0303", "rgba(148,163,184,0.15)"),
}
pts_mode = "all" if show_pts else "outliers"

fig_f3g1 = go.Figure()
for grp in grp_order:
    sub_d = df3_plot[df3_plot["Gruppe"] == grp]
    col, fill = COLORS_F3[grp]
    fig_f3g1.add_trace(go.Box(
        x=sub_d["listeners_plot"],
        name=grp,
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
    title="Last.fm listeners — Chart vs. Non-Chart Artists",
    xaxis_title="Last.fm listeners",
    template="plotly_dark",
    paper_bgcolor="#080b14", 
    plot_bgcolor="#161c2d",
    font=dict(color="white"),
    height=380,
    xaxis=dict(gridcolor="#232840"),
    yaxis=dict(gridcolor="#232840"),
    showlegend=False,
    boxmode="group",
)

with g2:
    st.plotly_chart(fig_f3g1, use_container_width=True)

if u_p is not None:
    if u_p < 0.05:
        stat_text_f3 = (
            f"Mann-Whitney U test: U = {u_stat:.0f}, p = {u_p:.4f}. "
            f"The result is statistically significant, indicating a reliable difference in Last.fm listener counts "
            f"between Chart Artists and Non-Chart Artists."
        )
    else:
        stat_text_f3 = (
            f"Mann-Whitney U test: U = {u_stat:.0f}, p = {u_p:.4f}. "
            f"The result is not statistically significant, so the data do not provide reliable evidence "
            f"for a difference in listener counts between the two groups."
        )

    if u_p < 0.05:
        interp_text_f3 = (
            f"Artists who appeared in the sampled global Spotify Weekly Charts between Feb 2023 and Feb 2026 "
            f"have, on average, about {ratio:.1f}× more Last.fm listeners than Non-Chart Artists "
            f"({mean_c:,.0f} vs. {mean_nc:,.0f}). "
            f"This is consistent with the idea that Spotify chart success and Last.fm listener counts capture related aspects "
            f"of digital popularity, although the two groups still overlap substantially."
        )
    else:
        interp_text_f3 = (
            f"Chart Artists have about {ratio:.1f}× as many Last.fm listeners on average "
            f"({mean_c:,.0f} vs. {mean_nc:,.0f}), but the difference is not statistically significant. "
            f"In this dataset, Spotify chart status therefore does not provide clear evidence of a robust difference "
            f"in Last.fm audience size."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>📊 Statistical analysis</h4>
        <p>{stat_text_f3}</p>
    </div>
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>{interp_text_f3}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F3 — GRAPH 2: Histogram overlay — listener distribution of both groups
# ══════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title">📊 Graph 2 — Listener distribution: Chart vs. Non-Chart Artists</div>',
    unsafe_allow_html=True
)

st.markdown("""
This overlaid histogram compares the distribution of Last.fm listener counts for Chart Artists and Non-Chart Artists.
The x-axis shows listener count, while the y-axis shows either the number of artists or the percentage of artists in each listener range, depending on the selected setting.
If normalization is enabled, the histogram compares the relative shape of the two distributions rather than raw counts.
A distribution that lies further to the right indicates generally higher listener values.
""")

h1, h2 = st.columns([1, 3])
with h1:
    n_bins_f3 = st.slider("Bins", 15, 50, 30, key="f3_bins")
    norm_hist = st.checkbox("Normalized (percent)", value=True, key="f3_norm")

    st.markdown("")
    st.markdown("**Color legend**")

    st.markdown(
        """
        <div style="display:flex; align-items:center; margin-bottom:8px;">
            <span style="display:inline-block; width:14px; height:14px; background:#24f803; border-radius:3px; margin-right:8px;"></span>
            <span>In Spotify Chart ✅</span>
        </div>
        <div style="display:flex; align-items:center;">
            <span style="display:inline-block; width:14px; height:14px; background:#fa0303; border-radius:3px; margin-right:8px;"></span>
            <span>Not in Chart ❌</span>
        </div>
        """,
        unsafe_allow_html=True
    )

df3_plot = df3.copy()
df3_plot["Gruppe"] = df3_plot["was_on_chart"].map(
    {True: "In Spotify Chart ✅", False: "Not in Chart ❌"}
)
df3_plot["listeners_plot"] = df3_plot["listeners"]

hist_mode = "percent" if norm_hist else ""

fig_f3g2 = go.Figure()
for grp, col in [("Not in Chart ❌", "#fa0303"), ("In Spotify Chart ✅", "#24f803")]:
    sub = df3_plot[df3_plot["Gruppe"] == grp]["listeners_plot"].dropna()
    fig_f3g2.add_trace(go.Histogram(
        x=sub,
        name=grp,
        histnorm=hist_mode,
        nbinsx=n_bins_f3,
        marker_color=col,
        opacity=0.65,
        hovertemplate=(
            f"{grp}<br>Listeners: %{{x:,.0f}}<br>Percent: %{{y:.2f}}%<extra></extra>"
            if norm_hist else
            f"{grp}<br>Listeners: %{{x:,.0f}}<br>Artists: %{{y}}<extra></extra>"
        ),
    ))

fig_f3g2.update_layout(
    barmode="overlay",
    title="Listener distribution — Chart vs. Non-Chart Artists",
    xaxis_title="Last.fm listeners",
    yaxis_title="Percent of artists" if norm_hist else "Number of artists",
    template="plotly_dark",
    paper_bgcolor="#080b14",
    plot_bgcolor="#161c2d",
    font=dict(color="white"),
    height=380,
    xaxis=dict(gridcolor="#232840"),
    yaxis=dict(gridcolor="#232840"),
    showlegend=False,
)

with h2:
    st.plotly_chart(fig_f3g2, use_container_width=True)

# Statistical analysis (descriptive complement to Graph 1)
if norm_hist:
    stat_text_f3g2 = (
        "This graph is a descriptive complement to the Mann-Whitney test in Graph 1. "
        "Because the histogram is normalized, the y-axis shows percentages rather than raw artist counts. "
        "This makes it easier to compare the shape and location of the two listener distributions directly."
    )
else:
    stat_text_f3g2 = (
        "This graph is a descriptive complement to the Mann-Whitney test in Graph 1. "
        "Without normalization, the histogram shows raw counts of artists in each listener range. "
        "This makes it easier to compare where the two groups are concentrated along the listener scale."
    )

# Interpretation
if u_p is not None and u_p < 0.05:
    interp_text_f3g2 = (
        "The distribution for Chart Artists is moderately shifted toward higher listener values, "
        "although the two groups still overlap substantially. "
        "This visually supports the result from Graph 1 that Chart Artists tend to have larger Last.fm audiences on average."
    )
else:
    interp_text_f3g2 = (
        "The two distributions overlap strongly, and any visible shift between them should be interpreted cautiously. "
        "Without a statistically significant group difference, the histogram alone does not support a robust conclusion about higher listener counts among Chart Artists."
    )

st.markdown(f"""
<div class="insight-card">
    <h4>📊 Statistical analysis</h4>
    <p>{stat_text_f3g2}</p>
</div>
<div class="insight-card">
    <h4>🔍 Interpretation</h4>
    <p>{interp_text_f3g2}</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F3 — GRAPH 3: Scatterplot chart intensity vs. listeners
# ══════════════════════════════════════════════════════════════════════════
if "chart_weeks" in df3.columns and df3["chart_weeks"].notna().sum() >= 5:

    st.markdown(
        '<div class="section-title">📈 Graph 3 — Chart intensity vs. Last.fm listeners</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    This scatterplot includes only artists who appeared in the sampled global Spotify Weekly Charts between February 2023 and February 2026.
    The x-axis shows either the number of chart weeks or total chart streams, while the y-axis shows current Last.fm listener counts.
    Logarithmic scaling can be enabled for either axis to compress very large values and make broad patterns easier to compare.
    The trend line summarizes whether stronger chart presence is associated with higher Last.fm audience size within the group of Chart Artists.
    """, unsafe_allow_html=True)


    # Control values are defined here and rendered later next to the chart
    x_metric_f3 = st.session_state.get("f3_x", "chart_weeks")
    log_x_f3 = st.session_state.get("f3_logx", True)
    log_y_f3 = st.session_state.get("f3_logy", True)
    lbl_f3 = st.session_state.get("f3_lbl", False)


    # Data preparation
    x_metric_f3 = st.session_state.get("f3_x", x_metric_f3)
    log_x_f3 = st.session_state.get("f3_logx", log_x_f3)
    log_y_f3 = st.session_state.get("f3_logy", log_y_f3)
    lbl_f3 = st.session_state.get("f3_lbl", lbl_f3)

    df_sc3 = df3.dropna(subset=[x_metric_f3, "listeners"]).copy()
    df_sc3 = df_sc3[df_sc3["was_on_chart"]]

    df_sc3["x_plot"] = np.log10(df_sc3[x_metric_f3] + 1) if log_x_f3 else df_sc3[x_metric_f3]
    df_sc3["y_plot"] = np.log10(df_sc3["listeners"] + 1) if log_y_f3 else df_sc3["listeners"]


    if len(df_sc3) >= 5:

        r_f3, p_f3 = stats.pearsonr(df_sc3["x_plot"], df_sc3["y_plot"])
        r2_f3 = r_f3 ** 2
        abs_r_f3 = abs(r_f3)


        # KPI boxes — must appear above the chart title/plot
        st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("N chart artists", len(df_sc3))
        k2.metric("Pearson r", f"{r_f3:.3f}")
        k3.metric("R²", f"{r2_f3:.1%}")
        k4.metric(
            "p-value",
            f"{p_f3:.4f}",
            delta="significant" if p_f3 < 0.05 else "not significant",
            delta_color="normal" if p_f3 < 0.05 else "inverse"
        )
        st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

        s1, s2 = st.columns([1, 3])

        with s1:
            st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)
            x_metric_f3 = st.radio(
                "X-axis",
                ["chart_weeks", "total_chart_streams"],
                index=0 if x_metric_f3 == "chart_weeks" else 1,
                key="f3_x",
                format_func=lambda x: {
                    "chart_weeks": "Weeks in chart",
                    "total_chart_streams": "Total streams"
                }[x],
            )
            log_x_f3 = st.checkbox("Log X", value=log_x_f3, key="f3_logx")
            log_y_f3 = st.checkbox("Log Y", value=log_y_f3, key="f3_logy")
            lbl_f3 = st.checkbox("Show names", value=lbl_f3, key="f3_lbl")


        # Relationship interpretation
        if abs_r_f3 < 0.1:
            relationship_text_f3 = "no meaningful linear relationship"
        elif abs_r_f3 < 0.3:
            relationship_text_f3 = f"a weak {'positive' if r_f3 > 0 else 'negative'} relationship"
        elif abs_r_f3 < 0.5:
            relationship_text_f3 = f"a moderate {'positive' if r_f3 > 0 else 'negative'} relationship"
        else:
            relationship_text_f3 = f"a strong {'positive' if r_f3 > 0 else 'negative'} relationship"


        # Regression line
        coef_f3 = np.polyfit(df_sc3["x_plot"], df_sc3["y_plot"], 1)
        x_line_f3 = np.linspace(df_sc3["x_plot"].min(), df_sc3["x_plot"].max(), 200)
        y_line_f3 = np.polyval(coef_f3, x_line_f3)


        # Axis labels
        x_axis_label = {
            "chart_weeks": "Weeks in chart",
            "total_chart_streams": "Total chart streams"
        }[x_metric_f3]

        if log_x_f3:
            x_axis_label = f"log₁₀({x_axis_label})"

        y_axis_label = "Last.fm listeners"

        if log_y_f3:
            y_axis_label = "log₁₀(Last.fm listeners)"

        # Plot
        fig_f3g3 = px.scatter(
            df_sc3,
            x="x_plot",
            y="y_plot",
            hover_name="artist_name",
            hover_data={
                "x_plot": False,
                "y_plot": False,
                "listeners": ":,",
                x_metric_f3: True
            },
            color="listeners",
            color_continuous_scale="Viridis",
            text="artist_name" if lbl_f3 else None,
            labels={
                "x_plot": x_axis_label,
                "y_plot": y_axis_label,
            },
            title=f"Chart intensity vs. listeners",
            template="plotly_dark",
        )

        fig_f3g3.add_trace(go.Scatter(
            x=x_line_f3,
            y=y_line_f3,
            mode="lines",
            name="OLS",
            line=dict(color="#f59e0b", width=2.5),
            hoverinfo="skip",
        ))

        fig_f3g3.update_traces(
            marker=dict(size=9, opacity=0.85, line=dict(width=0.5, color="white")),
            selector=dict(mode="markers")
        )

        if lbl_f3:
            fig_f3g3.update_traces(
                textposition="top center",
                textfont=dict(size=8, color="white"),
                selector=dict(mode="markers+text")
            )

        fig_f3g3.update_layout(
            height=480,
            paper_bgcolor="#080b14",
            plot_bgcolor="#161c2d",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#232840"),
            yaxis=dict(gridcolor="#232840"),
            coloraxis_showscale=False,
        )

        with s2:
            st.plotly_chart(fig_f3g3, use_container_width=True)

        # Statistical explanation
        stat_text_f3g3 = (
            f"Pearson correlation: r = {r_f3:.3f}, p = {p_f3:.4f}, R² = {r2_f3:.1%}. "
        )

        if p_f3 < 0.05:
            stat_text_f3g3 += (
                f"The result is statistically significant and indicates {relationship_text_f3} "
                f"between chart intensity and Last.fm listener count within the Chart Artist group."
            )
        else:
            stat_text_f3g3 += (
                "The result is not statistically significant and does not provide reliable evidence "
                "for a linear relationship between chart intensity and Last.fm listener count within the Chart Artist group."
            )


        if abs_r_f3 < 0.1:
            interp_text_f3g3 = (
                "Within the group of Chart Artists, stronger chart presence does not systematically correspond "
                "to higher Last.fm listener counts. This suggests that chart intensity alone is not a useful predictor "
                "of cross-platform audience size."
            )
        elif p_f3 < 0.05 and r_f3 > 0:
            interp_text_f3g3 = (
                "Chart Artists with stronger chart presence tend to have higher Last.fm listener counts. "
                "This suggests that repeated or more intense chart success is associated with somewhat broader audience reach across platforms, "
                "although the effect remains limited."
            )
        elif p_f3 < 0.05 and r_f3 < 0:
            interp_text_f3g3 = (
                "Chart Artists with stronger chart presence tend to have lower Last.fm listener counts. "
                "This indicates a negative association within the Chart Artist group, although the practical meaning should be interpreted with caution."
            )
        else:
            interp_text_f3g3 = (
                f"The observed pattern points to {relationship_text_f3}, but the result is not statistically significant. "
                "This means the apparent trend should be interpreted cautiously and may reflect random variation within the Chart Artist sample."
            )

        st.markdown(f"""
        <div class="insight-card">
            <h4>📊 Statistical analysis</h4>
            <p>{stat_text_f3g3}</p>
        </div>
        <div class="insight-card">
            <h4>🔍 Interpretation</h4>
            <p>{interp_text_f3g3}</p>
        </div>
        """, unsafe_allow_html=True)


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
    if u_p < 0.05:
        rq3_answer = (
            f"Artists who appeared in the global Spotify Weekly Charts between Feb 2023 and Feb 2026 "
            f"have, on average, about {ratio:.1f}× more Last.fm listeners than Non-Chart Artists "
            f"({mean_c:,.0f} vs. {mean_nc:,.0f}). "
            f"The difference is statistically significant (Mann-Whitney U, p = {u_p:.4f}). "
            f"This is consistent with the hypothesis that Spotify chart success and Last.fm listener counts "
            f"capture related aspects of digital popularity, although the two groups still overlap substantially."
        )
    else:
        rq3_answer = (
            f"Artists who appeared in the global Spotify Weekly Charts between Feb 2023 and Feb 2026 "
            f"have, on average, about {ratio:.1f}× as many Last.fm listeners as Non-Chart Artists "
            f"({mean_c:,.0f} vs. {mean_nc:,.0f}). "
            f"However, the difference is not statistically significant (Mann-Whitney U, p = {u_p:.4f}). "
            f"In this dataset, Spotify chart status does not provide clear evidence of a robust difference "
            f"in Last.fm listener counts between the two groups."
        )

    st.markdown(f"""<div class="insight-card">
        <h4>🎯 Answer to Research Question 3</h4>
        <p>{rq3_answer}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""<div class="methodology-note">
    <p>
    Chart assignment is based on normalized artist names (lowercase, trimmed). 
    In collaborations, each credited artist is counted separately. 
    The analysis uses sampled global Spotify Weekly Charts from February 2023 to February 2026, 
    with one representative chart week per month. 
    Last.fm listener counts are based on a March 2026 snapshot. 
    Mann-Whitney U was used because listener distributions are strongly right-skewed.
    </p>
</div>
""", unsafe_allow_html=True)
