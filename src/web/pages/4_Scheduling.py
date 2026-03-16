import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.styles import apply_styles
from components.navbar import render_navbar
from components.glossary import apply_glossary_styles, tt


def _hex_rgba(hex_color: str, alpha: float = 0.2) -> str:
    """Converts #rrggbb to rgba(r,g,b,alpha) for Plotly fillcolor."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


st.set_page_config(
    page_title="Market Time & Scheduling",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_styles()
render_navbar()
apply_glossary_styles()


# Load data
@st.cache_data
def load_data():
    p = "data/processed/final_dataset.csv"
    if not os.path.exists(p):
        return None
    df = pd.read_csv(p)
    for c in ["listeners", "playcount", "total_events",
              "avg_days_between_shows", "pct_weekend", "lead_time_days"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


df = load_data()

# Header
st.markdown("""
<div class="page-header">
    <div class="page-header-title-row">
        <span class="page-header-icon">📅</span>
        <span class="page-header-title">Market Time &amp; Scheduling</span>
    </div>
    <p>How do artists plan their tours and is the structure of concert scheduling
    related to their digital popularity?</p>
</div>
""", unsafe_allow_html=True)

# Research question overview
st.markdown("""
<div style="background:#161c2d;border:1px solid #232840;border-radius:14px;
    padding:24px 28px;margin-bottom:28px;">
    <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;
        letter-spacing:.12em;color:#475569 !important;margin-bottom:14px;">
        Table of Contents — Research Questions
    </div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <a href="#sched-1" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">1</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                How does average days between concerts differ between high and low Last.fm listener count artists?
            </span>
        </a>
        <a href="#sched-2" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">2</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                To what extent does an artist's Last.fm playcount influence the percentage of concerts scheduled on weekends?
            </span>
        </a>
        <a href="#sched-3" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">3</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                How does lead time (days between sale start and the first concert date)  correlate with an artist's Last.fm listener count?
            </span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

if df is None:
    st.error("File `data/processed/final_dataset.csv` not found.")
    st.code("python scripts/join_data.py", language="bash")
    st.stop()

# KPI summary
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Artists", len(df))
if "avg_days_between_shows" in df.columns:
    k2.metric("Avg. days between shows",
              f"{df['avg_days_between_shows'].median():.0f} days",
              help="Median across all artists")
if "pct_weekend" in df.columns:
    k3.metric("Avg. weekend share",
              f"{df['pct_weekend'].mean():.1f}%",
              help="Share of concerts Fri/Sat/Sun")
if "lead_time_days" in df.columns:
    k4.metric("Avg. lead time",
              f"{df['lead_time_days'].mean():.0f} days",
              help="Days between ticket sale start and concert")
k5.metric("Avg. Last.fm listeners",
          f"{int(df['listeners'].mean()):,}" if "listeners" in df.columns else "—")
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# QUESTION 1 — Days between shows vs. popularity
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div id="sched-1"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="rq-box">
    <h3>📅 Research Question 1</h3>
    <p>How does average days between concerts differ between high and low Last.fm listener count artists?
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Artists with large fan bases may be able to tour more frequently — or perhaps the opposite is true,
because major stars need more time for production, recovery, and global logistics.
This question examines the relationship between Last.fm listeners and the
average gap between two concerts.

**Hypothesis:** Popular artists tour on a tighter schedule (fewer days between shows),
because larger management teams enable more efficient planning and demand is higher.
""")

col_f1 = "avg_days_between_shows"

if col_f1 not in df.columns or df[col_f1].notna().sum() < 10:
    st.warning("Column `avg_days_between_shows` not found in the dataset — run join_data.py again.")
else:
    df1 = df.dropna(subset=["listeners", col_f1]).copy()
    df1 = df1[df1[col_f1] > 0]
    df1["log_listeners"] = np.log10(df1["listeners"] + 1)
    df1["Popularity-Tier"] = pd.qcut(df1["listeners"], q=4,
                                     labels=["Q1\n(niedrig)", "Q2", "Q3", "Q4\n(hoch)"])

    r1, p1 = stats.pearsonr(df1["log_listeners"], df1[col_f1])
    r1_s, p1_s = stats.spearmanr(df1["listeners"], df1[col_f1])
    coef1 = np.polyfit(df1["log_listeners"], df1[col_f1], 1)
    x_line1 = np.linspace(df1["log_listeners"].min(), df1["log_listeners"].max(), 200)
    y_line1 = np.polyval(coef1, x_line1)

    m1a, m1b, m1c, m1d = st.columns(4)

    artists_analyzed_q1 = len(df1)
    total_concerts_q1 = int(df1["total_events"].sum()) if "total_events" in df1.columns else None
    median_days_between_q1 = float(df1[col_f1].median()) if col_f1 in df1.columns else None
    median_concerts_per_artist_q1 = float(df1["total_events"].median()) if "total_events" in df1.columns else None

    m1a.metric("Artists analyzed", artists_analyzed_q1)
    m1b.metric("Total concerts analyzed", f"{total_concerts_q1}" if total_concerts_q1 is not None else "—")
    m1c.metric("Median days between shows", f"{median_days_between_q1:.1f}" if median_days_between_q1 is not None else "—")
    m1d.metric("Median concerts per artist", f"{median_concerts_per_artist_q1:.0f}" if median_concerts_per_artist_q1 is not None else "—")

    st.divider()
    # Graph 1a: Scatterplot
    st.markdown(
        '<div class="section-title">📈 Graph 1 — Listeners vs. days between shows</div>',
        unsafe_allow_html=True
    )

    graph1_descriptions = {
        "total_events": (
            "Each point represents one artist. The x-axis shows Last.fm listener count and the y-axis shows the average number of days between consecutive concerts. "
            "A logarithmic x-axis can be enabled to compress very large listener values and make broad patterns easier to compare. "
            "The points are colored by the total number of concerts in the dataset. This makes it easier to see whether artists with denser touring schedules also tend to have more total live events overall."
        ),
        "pct_weekend": (
            "Each point represents one artist. The x-axis shows Last.fm listener count and the y-axis shows the average number of days between consecutive concerts. "
            "A logarithmic x-axis can be enabled to compress very large listener values and make broad patterns easier to compare. "
            "The points are colored by weekend share — the percentage of concerts that take place on Fridays, Saturdays, or Sundays. This helps reveal whether tighter or more spread-out tour schedules are associated with stronger weekend concentration."
        ),
        "lead_time_days": (
            "Each point represents one artist. The x-axis shows Last.fm listener count and the y-axis shows the average number of days between consecutive concerts. "
            "A logarithmic x-axis can be enabled to compress very large listener values and make broad patterns easier to compare. "
            "The points are colored by lead time — the number of days between ticket sale start and the first concert date. This helps show whether artists with longer planning horizons also tend to space their concerts differently."
        ),
    }

    description_placeholder_1 = st.empty()

    g1_ctrl, g1_plot = st.columns([1, 3])
    with g1_ctrl:
        max_days = st.slider(
            "Max. days shown",
            30,
            200,
            min(200, int(df1[col_f1].quantile(0.95))),
            key="f7_max"
        )
        log_x1 = st.checkbox("Log X (listeners)", value=True, key="f7_logx")
        show_lbl1 = st.checkbox("Show names", False, key="f7_lbl")
        color_by1 = st.selectbox(
            "Color by",
            ["total_events", "pct_weekend", "lead_time_days"],
            format_func=lambda x: {
                "total_events": "Number of events",
                "pct_weekend": "Weekend share",
                "lead_time_days": "Lead time",
            }.get(x, x),
            key="f7_color"
        )
        color_by1 = color_by1 if color_by1 in df1.columns else None
    description_placeholder_1.markdown(graph1_descriptions[color_by1])

    df1_plot = df1[df1[col_f1] <= max_days].copy()

    # Dynamic x-axis column
    df1_plot["x_plot"] = np.log10(df1_plot["listeners"] + 1) if log_x1 else df1_plot["listeners"]

    if len(df1_plot) >= 5:
        # Recompute statistics on filtered data
        r1_plot, p1_plot = stats.pearsonr(df1_plot["x_plot"], df1_plot[col_f1])
        r2_1_plot = r1_plot ** 2
        abs_r1_plot = abs(r1_plot)

        if abs_r1_plot < 0.1:
            relationship_text_1 = "no meaningful linear relationship"
        elif abs_r1_plot < 0.3:
            relationship_text_1 = f"a weak {'positive' if r1_plot > 0 else 'negative'} relationship"
        elif abs_r1_plot < 0.5:
            relationship_text_1 = f"a moderate {'positive' if r1_plot > 0 else 'negative'} relationship"
        else:
            relationship_text_1 = f"a strong {'positive' if r1_plot > 0 else 'negative'} relationship"

        # Trend line based on filtered data
        coef1_plot = np.polyfit(df1_plot["x_plot"], df1_plot[col_f1], 1)
        x_line1_plot = np.linspace(df1_plot["x_plot"].min(), df1_plot["x_plot"].max(), 200)
        y_line1_plot = np.polyval(coef1_plot, x_line1_plot)

        x_axis_label = "log₁₀(Last.fm listeners)" if log_x1 else "Last.fm listeners"

        fig1 = px.scatter(
            df1_plot,
            x="x_plot",
            y=col_f1,
            color=color_by1 if color_by1 else "Popularity-Tier",
            color_continuous_scale="Viridis" if color_by1 else None,
            hover_name="artist_name",
            hover_data={
                "x_plot": False,
                col_f1: ":.1f",
                "listeners": ":,",
                "total_events": True
            },
            text="artist_name" if show_lbl1 else None,
            labels={
                "x_plot": x_axis_label,
                col_f1: "Avg. days between shows"
            },
            title=f"Listeners vs. avg. days between shows  |  number of artists = {len(df1_plot)}",
            template="plotly_dark",
        )

        fig1.add_trace(go.Scatter(
            x=x_line1_plot,
            y=y_line1_plot,
            mode="lines",
            name="trend line",
            line=dict(color="#10b981", width=2.5),
            hoverinfo="skip",
        ))

        if show_lbl1:
            fig1.update_traces(
                textposition="top center",
                textfont=dict(size=7, color="white"),
                selector=dict(mode="markers+text")
            )

        fig1.update_layout(
            height=460,
            paper_bgcolor="#080b14",
            plot_bgcolor="#161c2d",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#232840"),
            yaxis=dict(gridcolor="#232840"),
        )

        with g1_plot:
            st.plotly_chart(fig1, use_container_width=True)

        # Interpretation
        if abs_r1_plot < 0.1:
            interp_text_1 = (
                "Most artists cluster in the lower part of the chart, especially between about 0 and 15 days between shows. "
                "This means that for most artists in the dataset, concerts are scheduled relatively close together and long average breaks are less common. "
                "At the same time, the points are spread quite similarly across the x-axis, and the trend line is almost flat. "
                "In practice, this suggests that artists with more Last.fm listeners do not consistently have either tighter or looser touring schedules than artists with fewer listeners."
            )
        elif p1_plot < 0.05 and r1_plot > 0:
            interp_text_1 = (
                "Most artists are still concentrated in the lower part of the chart, which means relatively short breaks between concerts are common overall. "
                "However, the upward trend line suggests that artists with more Last.fm listeners tend to have somewhat longer average gaps between shows. "
                "This may indicate that larger artists follow slightly more spaced-out touring schedules, possibly because of bigger productions or more complex logistics."
            )
        elif p1_plot < 0.05 and r1_plot < 0:
            interp_text_1 = (
                "Most artists cluster in the lower range of the chart, but the downward trend line shows that artists with more Last.fm listeners tend to have even shorter gaps between concerts. "
                "This suggests that more popular artists may tour more intensively, with tighter schedules and more closely spaced performances."
            )
        else:
            interp_text_1 = (
                "Most artists are concentrated in the lower part of the chart, especially between about 0 and 15 days between shows, which indicates that compact touring schedules are common overall. "
                "Although the trend line shows a slight pattern, it is weak and not statistically strong. "
                "This means the visible difference between more popular and less popular artists should be interpreted cautiously and may simply reflect random variation in the data."
            )

        if color_by1 == "total_events":
            color_interp_1 = (
                " The color gradient additionally shows whether artists with more concerts cluster in a specific part of the chart. "
                "If brighter points appear mainly lower on the y-axis, this suggests that artists with more total shows also tend to follow tighter touring schedules."
            )
        elif color_by1 == "pct_weekend":
            color_interp_1 = (
                " The color pattern also helps show whether weekend-heavy touring is linked to tighter or more spread-out schedules. "
                "If similar colors appear throughout the chart, weekend concentration does not seem to be strongly connected to the spacing between concerts."
            )
        else:
            color_interp_1 = (
                " The color gradient also highlights whether artists with longer lead times tend to have more compact or more widely spaced touring schedules. "
                "If no clear color clustering appears, planning horizon and spacing between concerts likely operate largely independently."
            )

        interp_text_1 = interp_text_1 + color_interp_1

        st.markdown(f"""
        <div class="insight-card">
            <h4>🔍 Interpretation</h4>
            <p>{interp_text_1}</p>
        </div>
        """, unsafe_allow_html=True)


    else:
        st.warning("Too few data points after filtering to compute a reliable correlation.")
    
    st.divider()
    # ── Graph 1b: Box Plot by tier ─────────────────────────────────────────
    st.markdown(
        '<div class="section-title">📦 Graph 2 — Days between shows by popularity tier</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    Artists are sorted by Last.fm listener count and divided into four equally sized popularity tiers (quartiles).
    Each box shows the distribution of the average number of days between consecutive concerts within one tier.
    The line inside the box marks the median, the box contains the middle 50% of values, and the whiskers show the typical range.
    Points outside the whiskers are outliers.
    """)

    # Use the same filter as Graph 1
    df1b = df1[df1[col_f1] <= max_days].copy()

    # Robust tier handling
    def tier_rank(val: str) -> int:
        s = str(val).replace("\n", " ").lower()
        if "q1" in s:
            return 1
        if "q2" in s:
            return 2
        if "q3" in s:
            return 3
        if "q4" in s:
            return 4
        return 99

    def tier_label_en(val: str) -> str:
        s = str(val).replace("\n", " ").lower()
        if "q1" in s:
            return "Q1 (low)"
        if "q2" in s:
            return "Q2"
        if "q3" in s:
            return "Q3"
        if "q4" in s:
            return "Q4 (high)"
        return str(val).replace("\n", " ")

    present_tiers_raw = sorted(
        [t for t in df1b["Popularity-Tier"].dropna().unique()],
        key=tier_rank
    )

    present_tiers_display = [tier_label_en(t) for t in present_tiers_raw]

    tier_colors = {
        "Q1 (low)": "#1DB954",
        "Q2": "#7fb3d3",
        "Q3": "#f0c040",
        "Q4 (high)": "#e05050",
    }

    # Kruskal-Wallis on filtered data
    kw_groups = [
        df1b[df1b["Popularity-Tier"] == t][col_f1].dropna().values
        for t in present_tiers_raw
        if len(df1b[df1b["Popularity-Tier"] == t][col_f1].dropna()) > 1
    ]

    kw1_h = kw1_p = None
    if len(kw_groups) >= 2:
        kw1_h, kw1_p = stats.kruskal(*kw_groups)

    # Box plot
    fig1b = go.Figure()

    for raw_tier in present_tiers_raw:
        display_tier = tier_label_en(raw_tier)
        sub = df1b[df1b["Popularity-Tier"] == raw_tier][col_f1].dropna()
        if len(sub) == 0:
            continue

        fig1b.add_trace(go.Box(
            y=sub,
            name=display_tier,
            marker_color=tier_colors.get(display_tier, "#6366f1"),
            fillcolor=_hex_rgba(tier_colors.get(display_tier, "#6366f1")),
            line=dict(color=tier_colors.get(display_tier, "#6366f1"), width=1.5),
            boxpoints="outliers",
            hovertemplate=f"{display_tier}<br>Days: %{{y:.1f}}<extra></extra>",
        ))

    fig1b.update_layout(
        title="Days between shows by popularity tier",
        yaxis_title="Avg. days between shows",
        xaxis_title="Popularity tier (by Last.fm listeners)",
        template="plotly_dark",
        paper_bgcolor="#080b14",
        plot_bgcolor="#161c2d",
        font=dict(color="white"),
        height=420,
        xaxis=dict(
            gridcolor="#232840",
            categoryorder="array",
            categoryarray=present_tiers_display
        ),
        yaxis=dict(gridcolor="#232840"),
        showlegend=False,
    )

    st.plotly_chart(fig1b, use_container_width=True)

    # Tier summary table
    tier_table = (
        df1b.groupby("Popularity-Tier", observed=True)[col_f1]
        .agg(Mean="mean", Median="median", n="count")
        .round(1)
        .reset_index()
    )

    tier_table["Popularity-Tier"] = tier_table["Popularity-Tier"].apply(tier_label_en)
    tier_table["tier_rank"] = tier_table["Popularity-Tier"].map({
        "Q1 (low)": 1,
        "Q2": 2,
        "Q3": 3,
        "Q4 (high)": 4
    })
    tier_table = tier_table.sort_values("tier_rank").drop(columns="tier_rank")



    # Interpretation text
    median_map = {
        tier_label_en(row["Popularity-Tier"]): row["Median"]
        for _, row in (
            df1b.groupby("Popularity-Tier", observed=True)[col_f1]
            .agg(Median="median")
            .reset_index()
            .iterrows()
        )
    }

    q1_med = median_map.get("Q1 (low)")
    q4_med = median_map.get("Q4 (high)")

    if kw1_p is not None and kw1_p >= 0.05:
        interp_text_1b = (
            "The distributions of all popularity tiers overlap strongly. "
            "This means that popular and less popular artists show similar spacing between concerts."
        )
    elif kw1_p is not None and kw1_p < 0.05 and q1_med is not None and q4_med is not None:
        if q4_med < q1_med:
            interp_text_1b = (
                f"Artists in the highest popularity tier have shorter breaks between concerts "
                f"({q4_med:.1f} vs. {q1_med:.1f} days). "
                "This suggests that popular artists may tour more intensively."
            )
        elif q4_med > q1_med:
            interp_text_1b = (
                f"The box plots show that artists in the highest popularity tier (Q4) tend to have slightly longer gaps between concerts than artists in the lowest tier (Q1). "
                f"The median value for Q4 is around {q4_med:.1f} days, compared to roughly {q1_med:.1f} days for Q1. "
                "The wider spread in Q4 also shows that highly popular artists follow more varied touring schedules. "
                "Overall, the graph suggests that more popular artists may space their concerts further apart than less popular artists."
            )
        else:
            interp_text_1b = (
                "The median values are almost identical across tiers. "
                "Popularity does not appear to affect the spacing between concerts."
            )
    else:
        interp_text_1b = (
            "The grouped comparison does not show a clear pattern."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>{interp_text_1b}</p>
    </div>
    """, unsafe_allow_html=True)


    st.divider()
    # Summary: Research Question 1
    st.markdown(
        '<div class="section-title">Summary — Research Question 1: Days between shows</div>',
        unsafe_allow_html=True
    )

    summary_q1 = pd.DataFrame({
        "Metric": [
            "Artists included",
            "Metric",
            "Pearson r (Graph 1)",
            "p-value (Graph 1)",
            "Kruskal-Wallis p-value (Graph 2)",
        ],
        "Value": [
            len(df1),
            "Average days between shows",
            f"{r1_plot:.3f}" if "r1_plot" in locals() else "n/a",
            f"{p1_plot:.4f}" if "p1_plot" in locals() else "n/a",
            f"{kw1_p:.4f}" if kw1_p is not None else "n/a",
        ]
    })



    if "p1_plot" in locals():
        rq1_answer = (
            "The analysis shows that the average number of days between concerts is relatively similar across artists with different listener counts. "
            "Most artists perform shows within fairly compact touring schedules, often with less than two weeks between concerts. "
            "Although small differences appear between popularity tiers, the overall distributions overlap strongly. "
            "This suggests that digital popularity alone does not strongly determine how tightly concerts are scheduled, and other factors such as tour logistics, venue availability, and travel planning likely play a larger role."
        )
        st.markdown(f"""
        <div class="insight-card">
            <h4>🎯 Answer to Research Question 1</h4>
            <p>{rq1_answer}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    
# ══════════════════════════════════════════════════════════════════════════════
# QUESTION 2 — Weekend share vs. playcount
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div id="sched-2"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="rq-box">
    <h3>📅 Research Question 2</h3>
    <p>To what extent does an artist's Last.fm playcount influence the percentage of concerts scheduled on weekends?
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Weekends (Friday to Sunday) are more attractive for concert organizers —
more people are free, and tickets may sell better.
Do popular artists benefit from this advantage more often?
Or do less well-known artists rely more heavily on weekend dates,
because they need audiences who work during the week?

**Hypothesis:** Artists with high playcounts have a higher weekend share,
because their concerts are more profitable and organizers prefer prime time slots.
""")

col_f2_x = "playcount"
col_f2_y = "pct_weekend"

if col_f2_y not in df.columns or df[col_f2_y].notna().sum() < 10:
    st.warning("Column `pct_weekend` is not available.")
else:
    df2 = df.dropna(subset=[col_f2_x, col_f2_y]).copy()
    df2 = df2[df2[col_f2_x] > 0]
    df2["log_playcount"] = np.log10(df2[col_f2_x] + 1)
    df2["Popularity-Tier"] = pd.qcut(df2["listeners"], q=4,
                                     labels=["Q1\n(low)", "Q2", "Q3", "Q4\n(high)"])

    r2, p2 = stats.pearsonr(df2["log_playcount"], df2[col_f2_y])
    r2_s, p2_s = stats.spearmanr(df2[col_f2_x], df2[col_f2_y])
    coef2 = np.polyfit(df2["log_playcount"], df2[col_f2_y], 1)
    x_line2 = np.linspace(df2["log_playcount"].min(), df2["log_playcount"].max(), 200)
    y_line2 = np.polyval(coef2, x_line2)

    m2a, m2b, m2c, m2d = st.columns(4)

    artists_analyzed_q2 = len(df2)
    total_concerts_q2 = int(df2["total_events"].sum()) if "total_events" in df2.columns else None
    median_weekend_share_q2 = float(df2[col_f2_y].median()) if col_f2_y in df2.columns else None
    median_concerts_per_artist_q2 = float(df2["total_events"].median()) if "total_events" in df2.columns else None

    m2a.metric("Artists analyzed", artists_analyzed_q2)
    m2b.metric("Total concerts analyzed", f"{total_concerts_q2}" if total_concerts_q2 is not None else "—")
    m2c.metric("Median weekend share", f"{median_weekend_share_q2:.1f}%" if median_weekend_share_q2 is not None else "—")
    m2d.metric("Median concerts per artist", f"{median_concerts_per_artist_q2:.0f}" if median_concerts_per_artist_q2 is not None else "—")

    st.divider()
    # Graph 2a: Scatterplot
    st.markdown(
        '<div class="section-title">📈 Graph 1 — Playcount vs. weekend share</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    Each point represents one artist. The x-axis shows Last.fm playcount, and the y-axis shows the percentage of concerts scheduled on weekends.
    A logarithmic x-axis can be enabled to compress very large playcount values and make broad patterns easier to compare.
    The green trend line summarizes the overall linear relationship: if it slopes upward, artists with higher playcounts tend to have a higher weekend share; if it slopes downward, the opposite is true.
    The point colors indicate popularity tiers, which makes it easier to see whether different parts of the popularity range follow similar patterns.
    """)

    g2_ctrl, g2_plot = st.columns([1, 3])
    with g2_ctrl:
        log_x2 = st.checkbox("Log X (playcount)", value=True, key="f8_logx")
        show_lbl2 = st.checkbox("Show names", False, key="f8_lbl")

        st.markdown("")
        st.markdown("**Color legend**")

        if "f8_hist_q1" not in st.session_state:
            st.session_state["f8_hist_q1"] = True
        if "f8_hist_q2" not in st.session_state:
            st.session_state["f8_hist_q2"] = True
        if "f8_hist_q3" not in st.session_state:
            st.session_state["f8_hist_q3"] = True
        if "f8_hist_q4" not in st.session_state:
            st.session_state["f8_hist_q4"] = True

        st.markdown(
            """
            <div style="display:flex; align-items:center; margin-bottom:8px;">
                <span style="display:inline-block; width:14px; height:14px; background:#1DB954; border-radius:3px; margin-right:8px;"></span>
                <span>Q1 (low)</span>
            </div>
            <div style="display:flex; align-items:center; margin-bottom:8px;">
                <span style="display:inline-block; width:14px; height:14px; background:#7fb3d3; border-radius:3px; margin-right:8px;"></span>
                <span>Q2</span>
            </div>
            <div style="display:flex; align-items:center; margin-bottom:8px;">
                <span style="display:inline-block; width:14px; height:14px; background:#f0c040; border-radius:3px; margin-right:8px;"></span>
                <span>Q3</span>
            </div>
            <div style="display:flex; align-items:center;">
                <span style="display:inline-block; width:14px; height:14px; background:#e05050; border-radius:3px; margin-right:8px;"></span>
                <span>Q4 (high)</span>
            </div>
            <div style="display:flex; align-items:center; margin-top:10px;">
                <span style="display:inline-block; width:14px; height:3px; background:#10b981; margin-right:8px;"></span>
                <span>Trend line</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    df2_plot = df2.copy()
    df2_plot["x_plot"] = np.log10(df2_plot["playcount"] + 1) if log_x2 else df2_plot["playcount"]

    if len(df2_plot) >= 5:
        # Recompute statistics directly from the current data
        r2_plot, p2_plot = stats.pearsonr(df2_plot["x_plot"], df2_plot[col_f2_y])
        r2_sq_plot = r2_plot ** 2
        abs_r2_plot = abs(r2_plot)

        if abs_r2_plot < 0.1:
            relationship_text_2 = "no meaningful linear relationship"
        elif abs_r2_plot < 0.3:
            relationship_text_2 = f"a weak {'positive' if r2_plot > 0 else 'negative'} relationship"
        elif abs_r2_plot < 0.5:
            relationship_text_2 = f"a moderate {'positive' if r2_plot > 0 else 'negative'} relationship"
        else:
            relationship_text_2 = f"a strong {'positive' if r2_plot > 0 else 'negative'} relationship"

        # trend line
        coef2_plot = np.polyfit(df2_plot["x_plot"], df2_plot[col_f2_y], 1)
        x_line2_plot = np.linspace(df2_plot["x_plot"].min(), df2_plot["x_plot"].max(), 200)
        y_line2_plot = np.polyval(coef2_plot, x_line2_plot)

        x_axis_label = "log₁₀(Last.fm playcount)" if log_x2 else "Last.fm playcount"

        fig2 = px.scatter(
            df2_plot,
            x="x_plot",
            y=col_f2_y,
            color="Popularity-Tier",
            hover_name="artist_name",
            hover_data={
                "x_plot": False,
                col_f2_y: ":.1f",
                "playcount": ":,",
                "listeners": ":,"
            },
            text="artist_name" if show_lbl2 else None,
            labels={
                "x_plot": x_axis_label,
                col_f2_y: "Weekend share (%)"
            },
            title=f"Playcount vs. weekend share  |  r = {r2_plot:.3f}  |  n = {len(df2_plot)}",
            template="plotly_dark",
            category_orders={"Popularity-Tier": ["Q1\n(low)", "Q2", "Q3", "Q4\n(high)"]},
            color_discrete_sequence=["#1DB954", "#7fb3d3", "#f0c040", "#e05050"],
        )

        fig2.add_trace(go.Scatter(
            x=x_line2_plot,
            y=y_line2_plot,
            mode="lines",
            name="trend line",
            line=dict(color="#10b981", width=2.5),
            hoverinfo="skip",
        ))

        if show_lbl2:
            fig2.update_traces(
                textposition="top center",
                textfont=dict(size=7, color="white"),
                selector=dict(mode="markers+text")
            )

        fig2.update_layout(
            height=460,
            paper_bgcolor="#080b14",
            plot_bgcolor="#161c2d",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#232840"),
            yaxis=dict(gridcolor="#232840"),
            showlegend=False,
        )

        with g2_plot:
            st.plotly_chart(fig2, use_container_width=True)

        # Interpretation
        if abs_r2_plot < 0.1:
            interp_text_2 = (
                "Most points are spread across the chart without forming a clear upward or downward pattern. "
                "Artists with both low and high playcounts appear throughout the full range of weekend shares. "
                "The trend line is almost flat, which indicates that digital popularity on Last.fm does not strongly influence whether concerts are scheduled on weekends. "
                "In practice, both smaller and larger artists seem to rely on a similar mix of weekday and weekend shows."
            )
        elif p2_plot < 0.05 and r2_plot > 0:
            interp_text_2 = (
                "The points show a slight upward pattern and the trend line slopes upward. "
                "This suggests that artists with higher playcounts tend to have a somewhat higher percentage of concerts on weekends. "
                "A possible explanation is that more popular artists are more likely to receive prime weekend time slots when venues expect higher ticket demand."
            )
        elif p2_plot < 0.05 and r2_plot < 0:
            interp_text_2 = (
                "The trend line slopes slightly downward, meaning artists with higher playcounts tend to have a slightly lower weekend share. "
                "This could indicate that larger artists schedule concerts throughout the week as well, possibly because strong demand allows them to fill venues even on weekdays."
            )
        else:
            interp_text_2 = (
                "The chart shows a very weak pattern, but the points remain widely scattered and the relationship is not statistically strong. "
                "This means the visible trend should be interpreted cautiously and may simply reflect random variation between artists rather than a systematic scheduling strategy."
            )

        st.markdown(f"""
        <div class="insight-card">
            <h4>🔍 Interpretation</h4>
            <p>{interp_text_2}</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.warning("Too few data points to compute a reliable correlation.")

    st.divider()
    # Graph 2b: Histogram of weekend share
    st.markdown(
        '<div class="section-title">📊 Graph 2 — Distribution of weekend share</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    This histogram shows how weekend share is distributed across the popularity tiers.
    Each color represents one popularity tier, from Q1 (low) to Q4 (high). Because the histograms are overlaid, the tiers are distinguished by color rather than by separate axes.
    A value of 100% means that all concerts take place on weekends, while 0% means only weekdays.
    The plot helps compare whether different popularity tiers cluster around similar or different weekend-share ranges.
    """)

    h2_ctrl, h2_plot = st.columns([1, 3])
    with h2_ctrl:
        n_bins2 = st.slider("Bins", 10, 25, 20, key="f8_bins")
        norm_hist2 = st.checkbox("Normalized (percent)", value=True, key="f8_norm")

        st.markdown("""
        <div style="margin-top:4px;">
            <p style="color:#f1f5f9;font-weight:700;margin-bottom:14px;">Color legend</p>
            <div style="display:flex;align-items:center;margin-bottom:8px;">
                <span style="display:inline-block;width:14px;height:14px;background:#1DB954;border-radius:3px;margin-right:8px;"></span>
                <span>Q1 (low)</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:8px;">
                <span style="display:inline-block;width:14px;height:14px;background:#7fb3d3;border-radius:3px;margin-right:8px;"></span>
                <span>Q2</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:8px;">
                <span style="display:inline-block;width:14px;height:14px;background:#f0c040;border-radius:3px;margin-right:8px;"></span>
                <span>Q3</span>
            </div>
            <div style="display:flex;align-items:center;">
                <span style="display:inline-block;width:14px;height:14px;background:#e05050;border-radius:3px;margin-right:8px;"></span>
                <span>Q4 (high)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        show_q1_hist_f8 = True
        show_q2_hist_f8 = True
        show_q3_hist_f8 = True
        show_q4_hist_f8 = True

    hist_mode2 = "percent" if norm_hist2 else ""

    fig2b = go.Figure()
    hist_tiers_f8 = [
        ("Q1\n(low)", "Q1 (low)", "#1DB954", show_q1_hist_f8),
        ("Q2", "Q2",             "#7fb3d3", show_q2_hist_f8),
        ("Q3", "Q3",             "#f0c040", show_q3_hist_f8),
        ("Q4\n(high)", "Q4 (high)", "#e05050", show_q4_hist_f8),
    ]

    for raw_tier, display_tier, tier_color, tier_visible in hist_tiers_f8:
        if not tier_visible:
            continue
        sub = df2[df2["Popularity-Tier"] == raw_tier][col_f2_y].dropna()
        if len(sub) == 0:
            continue

        fig2b.add_trace(go.Histogram(
            x=sub,
            name=display_tier,
            nbinsx=n_bins2,
            histnorm=hist_mode2,
            marker_color=tier_color,
            opacity=0.65,
            hovertemplate=(
                f"{display_tier}<br>Weekend share: %{{x:.1f}}%<br>Percent: %{{y:.2f}}%<extra></extra>"
                if norm_hist2 else
                f"{display_tier}<br>Weekend share: %{{x:.1f}}%<br>Artists: %{{y}}<extra></extra>"
            ),
            showlegend=False,
        ))

    fig2b.update_layout(
        barmode="overlay",
        title="Distribution of weekend share by popularity tier",
        xaxis_title="Weekend share (%)",
        yaxis_title="Percent of artists" if norm_hist2 else "Number of artists",
        template="plotly_dark",
        paper_bgcolor="#080b14",
        plot_bgcolor="#161c2d",
        font=dict(color="white"),
        height=360,
        xaxis=dict(gridcolor="#232840"),
        yaxis=dict(gridcolor="#232840"),
        showlegend=False,
    )

    with h2_plot:
        st.plotly_chart(fig2b, use_container_width=True)

    # Weekend statistics table
    tier_means2 = (
        df2.groupby("Popularity-Tier", observed=True)[col_f2_y]
        .agg(Mean="mean", Median="median", n="count")
        .round(1)
        .reset_index()
    )

    tier_means2["Popularity-Tier"] = tier_means2["Popularity-Tier"].replace({
        "Q1\n(low)": "Q1 (low)",
        "Q4\n(high)": "Q4 (high)"
    })

    tier_order2 = {"Q1 (low)": 1, "Q2": 2, "Q3": 3, "Q4 (high)": 4}
    tier_means2["tier_order"] = tier_means2["Popularity-Tier"].map(tier_order2)
    tier_means2 = tier_means2.sort_values("tier_order").drop(columns="tier_order")



    # Interpretation
    median_map2 = dict(zip(tier_means2["Popularity-Tier"], tier_means2["Median"]))
    q1_med2 = median_map2.get("Q1 (low)")
    q4_med2 = median_map2.get("Q4 (high)")

    if q1_med2 is not None and q4_med2 is not None:
        if abs(q4_med2 - q1_med2) < 3:
            interp_text_2b = (
                "The histogram shows that the colored distributions for the popularity tiers overlap strongly across most weekend-share values. "
                "Artists from both low and high popularity groups appear in similar ranges, especially between roughly 20% and 60% weekend share. "
                "Because the distributions look very similar and the medians are close, the graph suggests that popularity does not strongly influence whether concerts are scheduled on weekends."
            )
        elif q4_med2 > q1_med2:
            interp_text_2b = (
                f"The red bars representing the most popular artists (Q4) appear slightly shifted toward higher weekend-share values compared with the lowest tier (Q1). "
                f"The median weekend share is around {q4_med2:.1f}% for Q4 and {q1_med2:.1f}% for Q1. "
                "This pattern suggests that highly popular artists may perform somewhat more often on weekends, possibly because promoters schedule them in prime time slots when audience demand is highest."
            )
        else:
            interp_text_2b = (
                f"The histogram indicates that artists in the highest popularity tier tend to have a slightly lower weekend share than those in the lowest tier "
                f"({q4_med2:.1f}% vs. {q1_med2:.1f}%). "
                "This suggests that highly popular artists may perform more evenly throughout the week rather than concentrating their concerts mainly on weekends."
            )
    else:
        interp_text_2b = (
            "There are not enough observations across all popularity tiers to clearly compare the distributions of weekend shares."
        )

    st.markdown(f"""
<div class="insight-card">
    <h4>🔍 Interpretation</h4>
    <p>{interp_text_2b}</p>
</div>
""", unsafe_allow_html=True)

    st.divider()
    # Summary: Research Question 2
    st.markdown(
        '<div class="section-title">Summary — Research Question 2: Weekend share</div>',
        unsafe_allow_html=True
    )

    summary_q2 = pd.DataFrame({
        "Metric": [
            "Artists included",
            "Metric",
            "Pearson r (Graph 1)",
            "p-value (Graph 1)",
            "Median weekend share Q1",
            "Median weekend share Q4",
        ],
        "Value": [
            len(df2),
            "Weekend share (%)",
            f"{r2_plot:.3f}" if "r2_plot" in locals() else "n/a",
            f"{p2_plot:.4f}" if "p2_plot" in locals() else "n/a",
            f"{q1_med2:.1f}%" if "q1_med2" in locals() and q1_med2 is not None else "n/a",
            f"{q4_med2:.1f}%" if "q4_med2" in locals() and q4_med2 is not None else "n/a",
        ]
    })



    if "p2_plot" in locals():
        rq2_answer = (
            "The distribution of weekend shares is very similar across all popularity tiers. "
            "Artists with both low and high playcounts appear throughout the same weekend‑share ranges, and the overall pattern does not show a clear upward or downward trend. "
            "This indicates that digital popularity does not strongly influence whether concerts are scheduled on weekends. "
            "Instead, weekend scheduling appears to be a common strategy for artists across all popularity levels, likely because weekends generally attract larger audiences and higher ticket demand."
        )
        st.markdown(f"""
        <div class="insight-card">
            <h4>🎯 Answer to Research Question 2</h4>
            <p>{rq2_answer}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# QUESTION 3 — Lead time vs. listeners
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div id="sched-3"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="rq-box">
    <h3>📅 Research Question 3</h3>
    <p>How does lead time — the number of days between ticket sale start and the first concert date — relate to an artist's Last.fm listener count?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
This question examines whether more popular artists tend to announce concerts further in advance than less popular artists.
A longer lead time may reflect larger productions, more complex logistics, or longer promotional phases before the first show.

**Hypothesis:** Artists with more listeners may have longer lead times, because larger tours often require more planning and earlier ticket sales.

**Method:** Only artists with at least one **upcoming** concert and a valid `onsale_date` are included.
For each artist, lead time is defined as the number of days between the first ticket sale start and the first upcoming concert date.
To exclude implausible outliers, only lead times between **0 and 1095 days (3 years)** are used.
""")

col_f3 = "lead_time_days"

if col_f3 not in df.columns or df[col_f3].notna().sum() < 10:
    st.warning("Column `lead_time_days` is not available.")
else:
    df3 = df.dropna(subset=["listeners", col_f3]).copy()
    df3 = df3[
        (df3[col_f3] >= 0) &
        (df3[col_f3] <= 1095)
    ].copy()

    if len(df3) < 10:
        st.warning("Too few valid artists remain after filtering lead time to 0–1095 days.")
    else:
        df3["log_listeners"] = np.log10(df3["listeners"] + 1)
        df3["Popularity-Tier"] = pd.qcut(
            df3["listeners"],
            q=4,
            labels=["Q1\n(low)", "Q2", "Q3", "Q4\n(high)"]
        )

        r3, p3 = stats.pearsonr(df3["log_listeners"], df3[col_f3])
        r3_s, p3_s = stats.spearmanr(df3["listeners"], df3[col_f3])
        coef3 = np.polyfit(df3["log_listeners"], df3[col_f3], 1)
        x_line3 = np.linspace(df3["log_listeners"].min(), df3["log_listeners"].max(), 200)
        y_line3 = np.polyval(coef3, x_line3)

        m3a, m3b, m3c, m3d = st.columns(4)

        artists_analyzed_q3 = len(df3)
        total_concerts_q3 = int(df3["total_events"].sum()) if "total_events" in df3.columns else None
        median_lead_time_q3 = float(df3[col_f3].median()) if col_f3 in df3.columns else None
        median_concerts_per_artist_q3 = float(df3["total_events"].median()) if "total_events" in df3.columns else None

        m3a.metric("Artists analyzed", artists_analyzed_q3)
        m3b.metric("Total concerts analyzed", f"{total_concerts_q3}" if total_concerts_q3 is not None else "—")
        m3c.metric("Median lead time (days)", f"{median_lead_time_q3:.0f}" if median_lead_time_q3 is not None else "—")
        m3d.metric("Median concerts per artist", f"{median_concerts_per_artist_q3:.0f}" if median_concerts_per_artist_q3 is not None else "—")

        st.divider()
        # Graph 3a: Scatterplot
        st.markdown(
            '<div class="section-title">📈 Graph 1 — Listeners vs. lead time</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        Each point represents one artist. The x-axis shows Last.fm listener count, and the y-axis shows lead time in days.
        Lead time means the number of days between ticket sale start and the concert date.
        A logarithmic x-axis can be enabled to compress very large listener values and make broad patterns easier to compare.
        The green trend line summarizes the overall linear relationship: if it slopes upward, artists with more listeners tend to have longer lead times; if it slopes downward, the opposite is true.
        """)

        g3_ctrl, g3_plot = st.columns([1, 3])
        with g3_ctrl:
            max_lead = st.slider(
                "Max. lead time (days)",
                30,
                1095,
                int(df3[col_f3].quantile(0.95)),
                key="f9_max"
            )
            log_x3 = st.checkbox("Log X (listeners)", value=True, key="f9_logx")
            show_lbl3 = st.checkbox("Show names", False, key="f9_lbl")
            color_by3 = st.selectbox(
                "Color by",
                ["total_events", "avg_days_between_shows", "pct_weekend"],
                format_func=lambda x: {
                    "total_events": "Number of events",
                    "avg_days_between_shows": "Days between shows",
                    "pct_weekend": "Weekend share",
                }.get(x, x),
                key="f9_color"
            )
            color_by3 = color_by3 if color_by3 in df3.columns else None

        df3_plot = df3[df3[col_f3] <= max_lead].copy()
        df3_plot["x_plot"] = np.log10(df3_plot["listeners"] + 1) if log_x3 else df3_plot["listeners"]

        if len(df3_plot) >= 5:
            # Recompute statistics on currently visible data
            r3_plot, p3_plot = stats.pearsonr(df3_plot["x_plot"], df3_plot[col_f3])
            r2_3_plot = r3_plot ** 2
            abs_r3_plot = abs(r3_plot)

            if abs_r3_plot < 0.1:
                relationship_text_3 = "no meaningful linear relationship"
            elif abs_r3_plot < 0.3:
                relationship_text_3 = f"a weak {'positive' if r3_plot > 0 else 'negative'} relationship"
            elif abs_r3_plot < 0.5:
                relationship_text_3 = f"a moderate {'positive' if r3_plot > 0 else 'negative'} relationship"
            else:
                relationship_text_3 = f"a strong {'positive' if r3_plot > 0 else 'negative'} relationship"

            # trend line based on filtered data
            coef3_plot = np.polyfit(df3_plot["x_plot"], df3_plot[col_f3], 1)
            x_line3_plot = np.linspace(df3_plot["x_plot"].min(), df3_plot["x_plot"].max(), 200)
            y_line3_plot = np.polyval(coef3_plot, x_line3_plot)

            x_axis_label = "log₁₀(Last.fm listeners)" if log_x3 else "Last.fm listeners"

            fig3 = px.scatter(
                df3_plot,
                x="x_plot",
                y=col_f3,
                color=color_by3 if color_by3 else "Popularity-Tier",
                color_continuous_scale="Viridis" if color_by3 else None,
                hover_name="artist_name",
                hover_data={
                    "x_plot": False,
                    col_f3: ":.0f",
                    "listeners": ":,",
                    "total_events": True
                },
                text="artist_name" if show_lbl3 else None,
                labels={
                    "x_plot": x_axis_label,
                    col_f3: "Avg. lead time (days)"
                },
                title=f"Listeners vs. lead time  | n = {len(df3_plot)}",
                template="plotly_dark",
                category_orders={"Popularity-Tier": ["Q1\n(low)", "Q2", "Q3", "Q4\n(high)"]},
                color_discrete_sequence=["#475569", "#6366f1", "#818cf8", "#fbbf24"],
            )

            fig3.add_trace(go.Scatter(
                x=x_line3_plot,
                y=y_line3_plot,
                mode="lines",
                name="trend line",
                line=dict(color="#10b981", width=2.5),
                hoverinfo="skip",
            ))

            if show_lbl3:
                fig3.update_traces(
                    textposition="top center",
                    textfont=dict(size=7, color="white"),
                    selector=dict(mode="markers+text")
                )

            fig3.update_layout(
                height=460,
                paper_bgcolor="#080b14",
                plot_bgcolor="#161c2d",
                font=dict(color="white"),
                xaxis=dict(gridcolor="#232840"),
                yaxis=dict(gridcolor="#232840"),
            )

            with g3_plot:
                st.plotly_chart(fig3, use_container_width=True)

            
            # Interpretation
            if abs_r3_plot < 0.1:
                interp_text_3 = (
                    "Most artists appear across a similar range of lead times regardless of their listener count. "
                    "The points are widely scattered and the trend line is nearly flat. "
                    "This indicates that both smaller and more popular artists tend to announce concerts within a comparable timeframe before the event."
                )
            elif p3_plot < 0.05 and r3_plot > 0:
                interp_text_3 = (
                    "The upward trend line indicates that artists with more Last.fm listeners tend to announce concerts earlier. "
                    "This suggests that larger tours may require longer planning phases, potentially due to bigger venues, more complex logistics, or longer marketing campaigns."
                )
            elif p3_plot < 0.05 and r3_plot < 0:
                interp_text_3 = (
                    "The downward slope of the trend line suggests that more popular artists sometimes announce concerts closer to the event date. "
                    "This could indicate that strong demand allows these artists to sell tickets even with shorter announcement periods."
                )
            else:
                interp_text_3 = (
                    "Although a slight pattern is visible in the chart, the points remain widely scattered and the relationship is weak. "
                    "This means popularity alone is not a strong predictor of how far in advance concerts are announced."
                )

            st.markdown(f"""
            <div class="insight-card">
                <h4>🔍 Interpretation</h4>
                <p>{interp_text_3}</p>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.warning("Too few data points after filtering to compute a reliable correlation.")

        st.divider()
        # Graph 3b: Box Plot by tier
        st.markdown(
            '<div class="section-title">📦 Graph 2 — Lead time by popularity tier</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        Artists are first sorted by their Last.fm listener count and then divided into four equally sized groups (quartiles).
        Q1 contains the 25% of artists with the lowest listener counts, while Q4 contains the 25% with the highest listener counts.
        Each box shows the distribution of lead time within one tier. The line inside the box marks the median, the box contains the middle 50% of values, and the whiskers show the typical range.
        Points outside the whiskers are outliers.
        """)

        df3b = df3.copy()

        # Robust tier handling
        def tier_rank_f3(val: str) -> int:
            s = str(val).replace("\n", " ").lower()
            if "q1" in s:
                return 1
            if "q2" in s:
                return 2
            if "q3" in s:
                return 3
            if "q4" in s:
                return 4
            return 99

        def tier_label_f3(val: str) -> str:
            s = str(val).replace("\n", " ").lower()
            if "q1" in s:
                return "Q1 (low)"
            if "q2" in s:
                return "Q2"
            if "q3" in s:
                return "Q3"
            if "q4" in s:
                return "Q4 (high)"
            return str(val).replace("\n", " ")

        present_tiers_raw_f3 = sorted(
            [t for t in df3b["Popularity-Tier"].dropna().unique()],
            key=tier_rank_f3
        )

        present_tiers_display_f3 = [tier_label_f3(t) for t in present_tiers_raw_f3]

        tier_colors_f3 = {
            "Q1 (low)": "#1DB954",
            "Q2": "#7fb3d3",
            "Q3": "#f0c040",
            "Q4 (high)": "#e05050",
        }

        # Kruskal-Wallis on filtered data
        kw3_groups = [
            df3b[df3b["Popularity-Tier"] == t][col_f3].dropna().values
            for t in present_tiers_raw_f3
            if len(df3b[df3b["Popularity-Tier"] == t][col_f3].dropna()) > 1
        ]

        kw3_h = kw3_p = None
        if len(kw3_groups) >= 2:
            kw3_h, kw3_p = stats.kruskal(*kw3_groups)

        # Box plot
        fig3b = go.Figure()

        for raw_tier in present_tiers_raw_f3:
            display_tier = tier_label_f3(raw_tier)
            sub = df3b[df3b["Popularity-Tier"] == raw_tier][col_f3].dropna()
            if len(sub) == 0:
                continue

            fig3b.add_trace(go.Box(
                y=sub,
                name=display_tier,
                marker_color=tier_colors_f3.get(display_tier, "#6366f1"),
                fillcolor=_hex_rgba(tier_colors_f3.get(display_tier, "#6366f1")),
                line=dict(color=tier_colors_f3.get(display_tier, "#6366f1"), width=1.5),
                boxpoints="outliers",
                hovertemplate=f"{display_tier}<br>Lead time: %{{y:.0f}} days<extra></extra>",
            ))

        fig3b.update_layout(
            title="Lead time by popularity tier",
            yaxis_title="Avg. lead time (days)",
            xaxis_title="Popularity tier (by Last.fm listeners)",
            template="plotly_dark",
            paper_bgcolor="#080b14",
            plot_bgcolor="#161c2d",
            font=dict(color="white"),
            height=420,
            xaxis=dict(
                gridcolor="#232840",
                categoryorder="array",
                categoryarray=present_tiers_display_f3
            ),
            yaxis=dict(gridcolor="#232840"),
            showlegend=False,
        )

        st.plotly_chart(fig3b, use_container_width=True)

        # Tier summary table
        tier_table_f3 = (
            df3b.groupby("Popularity-Tier", observed=True)[col_f3]
            .agg(Mean="mean", Median="median", n="count")
            .round(1)
            .reset_index()
        )

        tier_table_f3["Popularity-Tier"] = tier_table_f3["Popularity-Tier"].apply(tier_label_f3)
        tier_table_f3["tier_rank"] = tier_table_f3["Popularity-Tier"].map({
            "Q1 (low)": 1,
            "Q2": 2,
            "Q3": 3,
            "Q4 (high)": 4
        })
        tier_table_f3 = tier_table_f3.sort_values("tier_rank").drop(columns="tier_rank")

        # Interpretation
        median_map_f3 = dict(zip(tier_table_f3["Popularity-Tier"], tier_table_f3["Median"]))
        q1_med_f3 = median_map_f3.get("Q1 (low)")
        q4_med_f3 = median_map_f3.get("Q4 (high)")

        if kw3_p is not None and kw3_p >= 0.05:
            interp_text_3b = (
                "The boxes for the different popularity tiers overlap strongly, which means artists across all listener ranges tend to announce concerts at similar times. "
                "In other words, popularity alone does not appear to strongly influence tour announcement timing."
            )
        elif kw3_p is not None and kw3_p < 0.05 and q1_med_f3 is not None and q4_med_f3 is not None:
            if q4_med_f3 > q1_med_f3:
                interp_text_3b = (
                    f"The box plot shows that artists in the highest popularity tier (Q4) generally have longer lead times than artists in the lowest tier (Q1). "
                    f"The median lead time for Q4 is about {q4_med_f3:.1f} days, compared with roughly {q1_med_f3:.1f} days for Q1. "
                    "Overall, the pattern suggests that more popular artists tend to plan and announce their tours earlier than less popular artists."
                )
            elif q4_med_f3 < q1_med_f3:
                interp_text_3b = (
                    f"Artists in the highest popularity tier tend to announce concerts slightly later "
                    f"({q4_med_f3:.1f} vs. {q1_med_f3:.1f} days). "
                    "This could indicate that strong fan demand allows popular artists to sell tickets even with shorter lead times."
                )
            else:
                interp_text_3b = (
                    "Lead times are nearly identical across all popularity tiers."
                )
        else:
            interp_text_3b = (
                "The comparison between popularity tiers does not reveal a consistent pattern in lead time."
            )


        st.markdown(f"""
        <div class="insight-card">
            <h4>🔍 Interpretation</h4>
            <p>{interp_text_3b}</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        # Summary: Research Question 3
        st.markdown(
            '<div class="section-title">Summary — Research Question 3: Lead time</div>',
            unsafe_allow_html=True
        )

        summary_q3 = pd.DataFrame({
            "Metric": [
                "Artists included",
                "Metric",
                "Pearson r (Graph 1)",
                "p-value (Graph 1)",
                "Kruskal-Wallis p-value (Graph 2)",
            ],
            "Value": [
                len(df3),
                "Lead time (days)",
                f"{r3_plot:.3f}" if "r3_plot" in locals() else "n/a",
                f"{p3_plot:.4f}" if "p3_plot" in locals() else "n/a",
                f"{kw3_p:.4f}" if kw3_p is not None else "n/a",
            ]
        })



        if "p3_plot" in locals():
            rq3_answer = (
                "The results suggest that artists with higher listener counts tend to announce concerts slightly earlier than less popular artists. "
                "In the box‑plot comparison, the most popular artists show somewhat longer median lead times and a wider range of announcement periods. "
                "This pattern indicates that larger artists may plan and promote their tours further in advance. "
                "Longer lead times may reflect more complex tour logistics, larger venues, and longer promotional phases required for major productions."
            )
            st.markdown(f"""
            <div class="insight-card">
                <h4>🎯 Answer to Research Question 3</h4>
                <p>{rq3_answer}</p>
            </div>
            """, unsafe_allow_html=True)
