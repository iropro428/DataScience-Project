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
    <h1>📅 Market Time &amp; Scheduling</h1>
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
    m1a.metric("n Artists", len(df1))
    m1b.metric("Pearson r", f"{r1:.3f}")
    m1c.metric("p-value", f"{p1:.4f}",
               delta="significant" if p1 < 0.05 else "not significant",
               delta_color="normal" if p1 < 0.05 else "inverse")
    m1d.metric("Spearman r", f"{r1_s:.3f}")

    # Graph 1a: Scatterplot
    st.markdown(
        '<div class="section-title">📈 Graph 1 — Listeners vs. days between shows</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    Each point represents one artist. The x-axis shows Last.fm listener count, and the y-axis shows the average number of days between consecutive concerts.
    A logarithmic x-axis can be enabled to compress very large listener values and make broad patterns easier to compare.
    The green OLS trend line summarizes the overall linear relationship: if it slopes downward, more popular artists tend to have shorter breaks between shows; if it slopes upward, they tend to have longer average gaps.
    The filters allow users to hide extreme outliers and explore whether the visible pattern remains stable.
    """)

    g1_ctrl, g1_plot = st.columns([1, 3])
    with g1_ctrl:
        max_days = st.slider(
            "Max. days shown",
            30,
            365,
            int(df1[col_f1].quantile(0.95)),
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

        # OLS line based on filtered data
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
            name="OLS",
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

        # Statistical analysis
        stat_text_1 = (
            f"Pearson correlation: r = {r1_plot:.3f}, p = {p1_plot:.4f}, R² = {r2_1_plot:.1%}. "
        )
        if p1_plot < 0.05:
            stat_text_1 += (
                f"The result is statistically significant and indicates {relationship_text_1} "
                f"between listener count and average days between shows in the currently visible data."
            )
        else:
            stat_text_1 += (
                "The result is not statistically significant and does not provide reliable evidence "
                "for a linear relationship between listener count and average days between shows in the currently visible data."
            )

        # Interpretation
        if abs_r1_plot < 0.1:
            interp_text_1 = (
                "Within the currently visible data, artists with more Last.fm listeners do not systematically have shorter or longer breaks between concerts. "
                "This suggests no meaningful overall linear relationship between popularity and the average spacing of shows."
            )
        elif p1_plot < 0.05 and r1_plot > 0:
            interp_text_1 = (
                "Within the currently visible data, artists with more Last.fm listeners tend to have longer average breaks between concerts. "
                "This suggests that greater popularity may be associated with less tightly packed schedules, although the result remains descriptive."
            )
        elif p1_plot < 0.05 and r1_plot < 0:
            interp_text_1 = (
                "Within the currently visible data, artists with more Last.fm listeners tend to have shorter gaps between concerts. "
                "This suggests that higher popularity may be associated with more intensive touring schedules."
            )
        else:
            interp_text_1 = (
                f"The visible pattern points to {relationship_text_1}, but the result is not statistically significant. "
                "This means the apparent trend should be interpreted cautiously and may reflect random variation or the effect of filtering."
            )

        st.markdown(f"""
        <div class="insight-card">
            <h4>📊 Statistical analysis</h4>
            <p>{stat_text_1}</p>
        </div>
        <div class="insight-card">
            <h4>🔍 Interpretation</h4>
            <p>{interp_text_1}</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.warning("Too few data points after filtering to compute a reliable correlation.")

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
        "Q1 (low)": "#475569",
        "Q2": "#6366f1",
        "Q3": "#818cf8",
        "Q4 (high)": "#fbbf24",
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

    st.dataframe(tier_table, use_container_width=True)

    # Statistical analysis text
    if kw1_h is not None and kw1_p is not None:
        if kw1_p < 0.05:
            stat_text_1b = (
                f"The Kruskal-Wallis test is statistically significant (H = {kw1_h:.2f}, p = {kw1_p:.4f}). "
                "This means the popularity tiers do not all show the same distribution of days between shows."
            )
        else:
            stat_text_1b = (
                f"The Kruskal-Wallis test is not statistically significant (H = {kw1_h:.2f}, p = {kw1_p:.4f}). "
                "This means the grouped data do not show a clear overall difference between the popularity tiers."
            )
    else:
        stat_text_1b = "Not enough valid groups were available to compute the Kruskal-Wallis test."

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
            "The tier distributions overlap strongly. Overall, the grouped view does not show a clear difference in the average spacing between concerts."
        )
    elif kw1_p is not None and kw1_p < 0.05 and q1_med is not None and q4_med is not None:
        if q4_med < q1_med:
            interp_text_1b = (
                f"The highest-popularity tier has a lower median than the lowest-popularity tier "
                f"({q4_med:.1f} vs. {q1_med:.1f} days). "
                "This suggests that more popular artists may perform with shorter breaks between shows."
            )
        elif q4_med > q1_med:
            interp_text_1b = (
                f"The highest-popularity tier has a higher median than the lowest-popularity tier "
                f"({q4_med:.1f} vs. {q1_med:.1f} days). "
                "This suggests that more popular artists may have longer average breaks between shows."
            )
        else:
            interp_text_1b = (
                "The tiers differ overall, but the median values are very similar. "
                "This suggests that any group differences are subtle rather than visually large."
            )
    else:
        interp_text_1b = (
            "The grouped comparison should be interpreted cautiously because the visible pattern is not strong enough for a clear conclusion."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>📊 Statistical analysis</h4>
        <p>{stat_text_1b}</p>
    </div>
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>{interp_text_1b}</p>
    </div>
    """, unsafe_allow_html=True)

    # Summary: Research Question 1
    st.markdown(
        '<div class="section-title">Summary — Research Question 1</div>',
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

    st.dataframe(summary_q1, use_container_width=True, hide_index=True)

    if "p1_plot" in locals():
        if p1_plot >= 0.05 and kw1_p is not None and kw1_p < 0.05:
            rq1_answer = (
                f"There is no meaningful overall linear relationship between Last.fm listener count and the average number of days between shows "
                f"(r = {r1_plot:.3f}, p = {p1_plot:.4f}). "
                f"However, the grouped comparison across popularity tiers is statistically significant (Kruskal-Wallis p = {kw1_p:.4f}), "
                f"which suggests that scheduling differences may exist between tiers even though the pattern is not well described by a simple linear trend."
            )
        elif p1_plot < 0.05:
            rq1_answer = (
                f"There is a statistically significant linear relationship between Last.fm listener count and the average number of days between shows "
                f"(r = {r1_plot:.3f}, p = {p1_plot:.4f}). "
                f"This suggests that popularity is related to tour spacing, although the relationship should still be interpreted with caution."
            )
        else:
            rq1_answer = (
                f"There is no meaningful linear relationship between Last.fm listener count and the average number of days between shows "
                f"(r = {r1_plot:.3f}, p = {p1_plot:.4f}). "
                f"In this dataset, popularity alone is not a useful predictor of how tightly concerts are spaced."
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
    m2a.metric("n Artists", len(df2))
    m2b.metric("Pearson r", f"{r2:.3f}")
    m2c.metric("p-value", f"{p2:.4f}",
               delta="significant" if p2 < 0.05 else "not significant",
               delta_color="normal" if p2 < 0.05 else "inverse")
    m2d.metric("Spearman ρ", f"{r2_s:.3f}")

    # Graph 2a: Scatterplot
    st.markdown(
        '<div class="section-title">📈 Graph 1 — Playcount vs. weekend share</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    Each point represents one artist. The x-axis shows Last.fm playcount, and the y-axis shows the percentage of concerts scheduled on weekends.
    A logarithmic x-axis can be enabled to compress very large playcount values and make broad patterns easier to compare.
    The green OLS trend line summarizes the overall linear relationship: if it slopes upward, artists with higher playcounts tend to have a higher weekend share; if it slopes downward, the opposite is true.
    The point colors indicate popularity tiers, which makes it easier to see whether different parts of the popularity range follow similar patterns.
    """)

    g2_ctrl, g2_plot = st.columns([1, 3])
    with g2_ctrl:
        log_x2 = st.checkbox("Log X (playcount)", value=True, key="f8_logx")
        show_lbl2 = st.checkbox("Show names", False, key="f8_lbl")

        st.markdown("")
        st.markdown("**Color legend**")

        st.markdown(
            """
            <div style="display:flex; align-items:center; margin-bottom:8px;">
                <span style="display:inline-block; width:14px; height:14px; background:#475569; border-radius:3px; margin-right:8px;"></span>
                <span>Q1 (low)</span>
            </div>
            <div style="display:flex; align-items:center; margin-bottom:8px;">
                <span style="display:inline-block; width:14px; height:14px; background:#6366f1; border-radius:3px; margin-right:8px;"></span>
                <span>Q2</span>
            </div>
            <div style="display:flex; align-items:center; margin-bottom:8px;">
                <span style="display:inline-block; width:14px; height:14px; background:#818cf8; border-radius:3px; margin-right:8px;"></span>
                <span>Q3</span>
            </div>
            <div style="display:flex; align-items:center;">
                <span style="display:inline-block; width:14px; height:14px; background:#fbbf24; border-radius:3px; margin-right:8px;"></span>
                <span>Q4 (high)</span>
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

        # OLS line
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
            color_discrete_sequence=["#475569", "#6366f1", "#818cf8", "#fbbf24"],
        )

        fig2.add_trace(go.Scatter(
            x=x_line2_plot,
            y=y_line2_plot,
            mode="lines",
            name="OLS",
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

        # Statistical analysis
        stat_text_2 = f"Pearson correlation: r = {r2_plot:.3f}, p = {p2_plot:.4f}, R² = {r2_sq_plot:.1%}. "
        if p2_plot < 0.05:
            stat_text_2 += (
                f"The result is statistically significant and indicates {relationship_text_2} "
                f"between playcount and weekend share."
            )
        else:
            stat_text_2 += (
                "The result is not statistically significant and does not provide reliable evidence "
                "for a linear relationship between playcount and weekend share."
            )

        # Interpretation
        if abs_r2_plot < 0.1:
            interp_text_2 = (
                "Artists with higher playcounts do not systematically have a higher or lower weekend share. "
                "In this dataset, weekend scheduling appears largely independent of digital popularity measured by playcount."
            )
        elif p2_plot < 0.05 and r2_plot > 0:
            interp_text_2 = (
                "Artists with higher playcounts tend to have a higher weekend share. "
                "This suggests that more digitally popular artists may receive more commercially attractive weekend slots."
            )
        elif p2_plot < 0.05 and r2_plot < 0:
            interp_text_2 = (
                "Artists with higher playcounts tend to have a lower weekend share. "
                "This suggests that greater digital popularity is associated with fewer weekend dates in this dataset."
            )
        else:
            interp_text_2 = (
                f"The visible pattern points to {relationship_text_2}, but the result is not statistically significant. "
                "This means the apparent trend should be interpreted cautiously."
            )

        st.markdown(f"""
        <div class="insight-card">
            <h4>📊 Statistical analysis</h4>
            <p>{stat_text_2}</p>
        </div>
        <div class="insight-card">
            <h4>🔍 Interpretation</h4>
            <p>{interp_text_2}</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.warning("Too few data points to compute a reliable correlation.")

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
        n_bins2 = st.slider("Bins", 10, 40, 20, key="f8_bins")
        norm_hist2 = st.checkbox("Normalized (percent)", value=True, key="f8_norm")

        st.markdown("")
        st.markdown("**Color legend**")

        st.markdown(
            """
            <div style="display:flex; align-items:center; margin-bottom:8px;">
                <span style="display:inline-block; width:14px; height:14px; background:#475569; border-radius:3px; margin-right:8px;"></span>
                <span>Q1 (low)</span>
            </div>
            <div style="display:flex; align-items:center; margin-bottom:8px;">
                <span style="display:inline-block; width:14px; height:14px; background:#6366f1; border-radius:3px; margin-right:8px;"></span>
                <span>Q2</span>
            </div>
            <div style="display:flex; align-items:center; margin-bottom:8px;">
                <span style="display:inline-block; width:14px; height:14px; background:#818cf8; border-radius:3px; margin-right:8px;"></span>
                <span>Q3</span>
            </div>
            <div style="display:flex; align-items:center;">
                <span style="display:inline-block; width:14px; height:14px; background:#fbbf24; border-radius:3px; margin-right:8px;"></span>
                <span>Q4 (high)</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    hist_mode2 = "percent" if norm_hist2 else ""

    fig2b = go.Figure()
    for tier, col in [("Q1\n(low)", "#475569"), ("Q2", "#6366f1"),
                      ("Q3", "#818cf8"), ("Q4\n(high)", "#fbbf24")]:
        sub = df2[df2["Popularity-Tier"] == tier][col_f2_y].dropna()
        if len(sub) == 0:
            continue

        fig2b.add_trace(go.Histogram(
            x=sub,
            name=tier.replace("\n", " "),
            nbinsx=n_bins2,
            histnorm=hist_mode2,
            marker_color=col,
            opacity=0.65,
            hovertemplate=(
                f"{tier.replace(chr(10), ' ')}<br>Weekend share: %{{x:.1f}}%<br>Percent: %{{y:.2f}}%<extra></extra>"
                if norm_hist2 else
                f"{tier.replace(chr(10), ' ')}<br>Weekend share: %{{x:.1f}}%<br>Artists: %{{y}}<extra></extra>"
            ),
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

    st.dataframe(tier_means2, use_container_width=True)

    # Interpretation
    median_map2 = dict(zip(tier_means2["Popularity-Tier"], tier_means2["Median"]))
    q1_med2 = median_map2.get("Q1 (low)")
    q4_med2 = median_map2.get("Q4 (high)")

    if q1_med2 is not None and q4_med2 is not None:
        if abs(q4_med2 - q1_med2) < 3:
            interp_text_2b = (
                "The distributions overlap strongly, and the median weekend share is fairly similar across the popularity tiers. "
                "This supports the idea that weekend scheduling does not differ much by popularity level."
            )
        elif q4_med2 > q1_med2:
            interp_text_2b = (
                f"The higher-popularity tier shows a somewhat higher median weekend share than the lowest tier "
                f"({q4_med2:.1f}% vs. {q1_med2:.1f}%). "
                "This suggests that more popular artists may appear slightly more often on weekends, although the overlap between tiers remains substantial."
            )
        else:
            interp_text_2b = (
                f"The higher-popularity tier shows a somewhat lower median weekend share than the lowest tier "
                f"({q4_med2:.1f}% vs. {q1_med2:.1f}%). "
                "This suggests that more popular artists do not necessarily rely more heavily on weekend slots."
            )
    else:
        interp_text_2b = (
            "The tier distributions should be interpreted cautiously because not all groups are clearly represented in the current view."
        )

    st.markdown(f"""
<div class="insight-card">
    <h4>🔍 Interpretation</h4>
    <p>{interp_text_2b}</p>
</div>
""", unsafe_allow_html=True)

    # Summary: Research Question 2
    st.markdown(
        '<div class="section-title">Summary — Research Question 2</div>',
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

    st.dataframe(summary_q2, use_container_width=True, hide_index=True)

    if "p2_plot" in locals():
        if p2_plot < 0.05:
            rq2_answer = (
                f"There is a statistically significant relationship between Last.fm playcount and weekend share "
                f"(r = {r2_plot:.3f}, p = {p2_plot:.4f}). "
                f"This suggests that digital popularity is related to how strongly concerts are concentrated on weekends."
            )
        else:
            rq2_answer = (
                f"There is no meaningful linear relationship between Last.fm playcount and weekend share "
                f"(r = {r2_plot:.3f}, p = {p2_plot:.4f}). "
                f"Artists with higher playcounts do not systematically have a higher or lower share of weekend concerts."
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
""")

st.info(
    "**Method:** Only artists with at least one **upcoming** concert and a valid `onsale_date` are included. "
    "For each artist, lead time is defined as the number of days between the first ticket sale start and the first upcoming concert date. "
    "To exclude implausible outliers, only lead times between **0 and 1095 days (3 years)** are used."
)

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
        m3a.metric("n Artists", len(df3))
        m3b.metric("Pearson r", f"{r3:.3f}")
        m3c.metric("p-value", f"{p3:.4f}",
                   delta="significant" if p3 < 0.05 else "not significant",
                   delta_color="normal" if p3 < 0.05 else "inverse")
        m3d.metric("Spearman ρ", f"{r3_s:.3f}")

        # Graph 3a: Scatterplot
        st.markdown(
            '<div class="section-title">📈 Graph 1 — Listeners vs. lead time</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        Each point represents one artist. The x-axis shows Last.fm listener count, and the y-axis shows lead time in days.
        Lead time means the number of days between ticket sale start and the concert date.
        A logarithmic x-axis can be enabled to compress very large listener values and make broad patterns easier to compare.
        The green OLS trend line summarizes the overall linear relationship: if it slopes upward, artists with more listeners tend to have longer lead times; if it slopes downward, the opposite is true.
        """)

        g3_ctrl, g3_plot = st.columns([1, 3])
        with g3_ctrl:
            max_lead = st.slider(
                "Max. lead time (days)",
                30,
                730,
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

            # OLS line based on filtered data
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
                title=f"Listeners vs. lead time  |  r = {r3_plot:.3f}  |  n = {len(df3_plot)}",
                template="plotly_dark",
                category_orders={"Popularity-Tier": ["Q1\n(low)", "Q2", "Q3", "Q4\n(high)"]},
                color_discrete_sequence=["#475569", "#6366f1", "#818cf8", "#fbbf24"],
            )

            fig3.add_trace(go.Scatter(
                x=x_line3_plot,
                y=y_line3_plot,
                mode="lines",
                name="OLS",
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

            # Statistical analysis
            stat_text_3 = f"Pearson correlation: r = {r3_plot:.3f}, p = {p3_plot:.4f}, R² = {r2_3_plot:.1%}. "
            if p3_plot < 0.05:
                stat_text_3 += (
                    f"The result is statistically significant and indicates {relationship_text_3} "
                    f"between listener count and lead time in the currently visible data."
                )
            else:
                stat_text_3 += (
                    "The result is not statistically significant and does not provide reliable evidence "
                    "for a linear relationship between listener count and lead time in the currently visible data."
                )

            # Interpretation
            if abs_r3_plot < 0.1:
                interp_text_3 = (
                    "Within the currently visible data, artists with more Last.fm listeners do not systematically have longer or shorter lead times. "
                    "This suggests no meaningful overall linear relationship between popularity and how far in advance concerts are announced."
                )
            elif p3_plot < 0.05 and r3_plot > 0:
                interp_text_3 = (
                    "Within the currently visible data, artists with more Last.fm listeners tend to have longer lead times. "
                    "This suggests that more popular artists may announce concerts further in advance."
                )
            elif p3_plot < 0.05 and r3_plot < 0:
                interp_text_3 = (
                    "Within the currently visible data, artists with more Last.fm listeners tend to have shorter lead times. "
                    "This suggests that higher popularity is associated with more short-notice concert announcements in this dataset."
                )
            else:
                interp_text_3 = (
                    f"The visible pattern points to {relationship_text_3}, but the result is not statistically significant. "
                    "This means the apparent trend should be interpreted cautiously."
                )

            st.markdown(f"""
            <div class="insight-card">
                <h4>📊 Statistical analysis</h4>
                <p>{stat_text_3}</p>
            </div>
            <div class="insight-card">
                <h4>🔍 Interpretation</h4>
                <p>{interp_text_3}</p>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.warning("Too few data points after filtering to compute a reliable correlation.")

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

        df3b = df3[df3[col_f3] <= max_lead].copy()

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
            "Q1 (low)": "#475569",
            "Q2": "#6366f1",
            "Q3": "#818cf8",
            "Q4 (high)": "#fbbf24",
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

        st.dataframe(tier_table_f3, use_container_width=True)

        # Statistical analysis
        if kw3_h is not None and kw3_p is not None:
            if kw3_p < 0.05:
                stat_text_3b = (
                    f"The Kruskal-Wallis test is statistically significant (H = {kw3_h:.2f}, p = {kw3_p:.4f}). "
                    "This means the popularity tiers do not all show the same distribution of lead time."
                )
            else:
                stat_text_3b = (
                    f"The Kruskal-Wallis test is not statistically significant (H = {kw3_h:.2f}, p = {kw3_p:.4f}). "
                    "This means the grouped data do not show a clear overall difference between the popularity tiers."
                )
        else:
            stat_text_3b = "Not enough valid groups were available to compute the Kruskal-Wallis test."

        # Interpretation
        median_map_f3 = dict(zip(tier_table_f3["Popularity-Tier"], tier_table_f3["Median"]))
        q1_med_f3 = median_map_f3.get("Q1 (low)")
        q4_med_f3 = median_map_f3.get("Q4 (high)")

        if kw3_p is not None and kw3_p >= 0.05:
            interp_text_3b = (
                "The tier distributions overlap strongly. Overall, the grouped view does not show a clear difference in lead time across the popularity tiers."
            )
        elif kw3_p is not None and kw3_p < 0.05 and q1_med_f3 is not None and q4_med_f3 is not None:
            if q4_med_f3 > q1_med_f3:
                interp_text_3b = (
                    f"The highest-popularity tier has a higher median lead time than the lowest-popularity tier "
                    f"({q4_med_f3:.1f} vs. {q1_med_f3:.1f} days). "
                    "This suggests that more popular artists may announce concerts further in advance."
                )
            elif q4_med_f3 < q1_med_f3:
                interp_text_3b = (
                    f"The highest-popularity tier has a lower median lead time than the lowest-popularity tier "
                    f"({q4_med_f3:.1f} vs. {q1_med_f3:.1f} days). "
                    "This suggests that more popular artists may not necessarily plan further ahead."
                )
            else:
                interp_text_3b = (
                    "The tiers differ overall, but the median values are very similar. "
                    "This suggests that any group differences are subtle rather than visually large."
                )
        else:
            interp_text_3b = (
                "The grouped comparison should be interpreted cautiously because the visible pattern is not strong enough for a clear conclusion."
            )


        st.markdown(f"""
        <div class="insight-card">
            <h4>📊 Statistical analysis</h4>
            <p>{stat_text_3b}</p>
        </div>
        <div class="insight-card">
            <h4>🔍 Interpretation</h4>
            <p>{interp_text_3b}</p>
        </div>
        """, unsafe_allow_html=True)

        # Summary: Research Question 3
        st.markdown(
            '<div class="section-title">Summary — Research Question 3</div>',
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

        st.dataframe(summary_q3, use_container_width=True, hide_index=True)

        if "p3_plot" in locals():
            if p3_plot >= 0.05 and kw3_p is not None and kw3_p < 0.05:
                rq3_answer = (
                    f"There is no meaningful overall linear relationship between Last.fm listener count and lead time "
                    f"(r = {r3_plot:.3f}, p = {p3_plot:.4f}). "
                    f"However, the grouped comparison across popularity tiers is statistically significant (Kruskal-Wallis p = {kw3_p:.4f}), "
                    f"which suggests that planning lead time may differ between tiers even though the pattern is not well described by a simple linear trend."
                )
            elif p3_plot < 0.05:
                rq3_answer = (
                    f"There is a statistically significant linear relationship between Last.fm listener count and lead time "
                    f"(r = {r3_plot:.3f}, p = {p3_plot:.4f}). "
                    f"This suggests that popularity is related to how far in advance concerts are announced."
                )
            else:
                rq3_answer = (
                    f"There is no meaningful linear relationship between Last.fm listener count and lead time "
                    f"(r = {r3_plot:.3f}, p = {p3_plot:.4f}). "
                    f"In this dataset, popularity alone is not a useful predictor of how far in advance concerts are announced."
                )

            st.markdown(f"""
            <div class="insight-card">
                <h4>🎯 Answer to Research Question 3</h4>
                <p>{rq3_answer}</p>
            </div>
            """, unsafe_allow_html=True)
