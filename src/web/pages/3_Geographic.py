import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import os

import sys as _sys, os as _os

from components.util import hex_rgba

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from components.styles import apply_styles
from components.navbar import render_navbar
from components.glossary import apply_glossary_styles, tt

st.set_page_config(
    page_title="Geographic Analysis",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
apply_styles()
render_navbar()
apply_glossary_styles()

# Header
st.markdown("""
<div class="page-header">
    <h1>🗺️ Geographic Analysis</h1>
    <p>Analysing touring patterns: revisit cities, capital preferences, and alignment between streaming reach and tour geography.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#121A2B;border:1px solid #27324A;border-radius:14px;
    padding:24px 28px;margin-bottom:28px; box-shadow:0 8px 24px rgba(0,0,0,.22);">
    <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;
        letter-spacing:.12em;color:#7C89A3 !important;margin-bottom:14px;">
        Table of Contents - Research Questions
    </div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <a href="#geo-frage-1" style="display:flex;align-items:flex-start;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">1</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                What is the ratio of revisit cities to new cities on an artist's current tour?
            </span>
        </a>
        <a href="#geo-frage-2" style="display:flex;align-items:flex-start;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">2</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                What proportion of an artist's performances take place in capital cities compared to non-capital cities?
            </span>
        </a>
        <a href="#geo-frage-3" style="display:flex;align-items:flex-start;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">3</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                How well do the countries where an artist has the highest listener reach on Last.fm align with the countries where they perform on their Ticketmaster tour?
            </span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="geo-frage-1"></div>', unsafe_allow_html=True)


# Load Data
@st.cache_data
def load_data():
    f1 = "data/processed/final_dataset.csv"
    f2 = "data/processed/f4_city_frequencies.csv"
    if not os.path.exists(f1):
        return None, None
    df = pd.read_csv(f1)
    for col in ["revisit_cities", "new_cities", "pct_revisit_cities",
                "revisit_ratio", "pct_events_revisit", "total_events",
                "listeners", "pct_capital"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    city_df = pd.read_csv(f2) if os.path.exists(f2) else None
    return df, city_df


df, city_df = load_data()

if df is None:
    st.error("⚠️  `data/processed/final_dataset.csv` nicht gefunden.")
    st.code("python scripts/join_data.py")
    st.stop()

F4_COLS = ["revisit_cities", "new_cities", "pct_revisit_cities", "revisit_ratio", "pct_events_revisit"]
if any(c not in df.columns for c in F4_COLS):
    st.error(f"⚠️  Daten für Frage 1 fehlen — `join_data.py` ausführen.")
    st.code("python scripts/join_data.py")
    st.stop()

df_f4 = df.dropna(subset=["revisit_cities", "new_cities"]).copy()

# Global Metrics
total_rev = df_f4["revisit_cities"].sum()
total_new = df_f4["new_cities"].sum()
total_cities = total_rev + total_new
global_ratio = total_rev / total_new if total_new > 0 else 0
global_pct = total_rev / total_cities * 100 if total_cities > 0 else 0
mean_pct = df_f4["pct_revisit_cities"].mean()
median_pct = df_f4["pct_revisit_cities"].median()

# Sidebar
with st.sidebar:
    st.markdown("## 🗺️ Geographic Analysis")
    st.divider()
    st.markdown("**▶ Q1 — Revisit vs New Cities**")
    st.markdown("F5 — Genre Density 300km")
    st.markdown("Q2 — Capital vs Non-Capital")
    st.divider()
    st.metric("Künstler gesamt", len(df))
    st.metric("mit Daten", len(df_f4))
    if city_df is not None:
        n_cities = city_df["city"].nunique()
        st.metric("Einzigartige Städte", n_cities)
    st.divider()
    st.markdown("**Graphs auf dieser Seite**")
    st.markdown("📈 Scatterplot · 📊 Balken · 📦 Boxplot · 🔍 Detail")

# ══════════════════════════════════════════════════════════════════════════
# RESEARCH QUESTION 1
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="rq-box">
    <h3>🗺️ Research Question 1</h3>
    <p>What is the ratio of revisit cities to new cities on an artist's current tour?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Definitions**

| Term | Meaning |
|------|---------|
| **New City** | A city the artist visited exactly **once** during the observation period |
| **Revisit City** | A city the artist visited **≥ 2 times** |
| **pct_revisit_cities** | Share of revisit cities out of all cities visited (%) |
| **revisit_ratio** | Revisit cities / new cities (ratio) |
| **pct_events_revisit** | Share of all events taking place in revisit cities (%) — typically higher than pct_revisit_cities since these cities count multiple times |

**Hypothesis:** Artists with larger tours tend to return to proven markets more often — optimising for reliable audiences. Smaller artists explore broader geographic territory.
""")

st.divider()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Avg. Revisit Rate", f"{mean_pct:.1f}%", delta=f"Median {median_pct:.1f}%")
k2.metric("Global Ratio", f"{global_ratio:.2f}", delta="revisit / new")
k3.metric("Total Revisit Cities", f"{total_rev:.0f}")
k4.metric("Total New Cities", f"{total_new:.0f}")
k5.metric("% of Touring = Revisit", f"{global_pct:.1f}%")
st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GRAPH 1 — Scatterplot Revisit vs. New Cities
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 1 — Revisit vs. New Cities per Artist</div>',
            unsafe_allow_html=True)

st.markdown("""
Each dot is one artist. The x-axis shows new cities visited, the y-axis shows revisit cities. 
Artists above the dashed diagonal revisit more cities than they explore new ones — a consolidation strategy. 
Artists below the line explore more new cities than they return to.
""")

s1, s2 = st.columns([1, 3])
with s1:
    min_ev = st.slider("Minimum events", 1, 20, 3, key="f4s_min")
    lbl_sc = st.checkbox("Show names", value=False, key="f4s_lbl")
    col_by = st.radio(
        "Color by",
        ["total_events", "pct_revisit_cities", "listeners"],
        index=0, key="f4s_col",
        format_func=lambda x: {
            "total_events": "Events",
            "pct_revisit_cities": "% Revisit",
            "listeners": "Listeners"
        }[x]
    )

df_s = df_f4[df_f4["total_events"] >= min_ev].dropna(subset=["new_cities", "revisit_cities"]).copy()
if col_by == "listeners" and "listeners" not in df_s.columns:
    col_by = "total_events"
df_s = df_s.dropna(subset=[col_by])

if len(df_s) > 0:
    df_s["x_p"] = df_s["new_cities"]
    df_s["y_p"] = df_s["revisit_cities"]
    max_diag = max(df_s["x_p"].max(), df_s["y_p"].max()) * 1.05

    fig1 = px.scatter(
        df_s, x="x_p", y="y_p",
        color=col_by,
        color_continuous_scale="YlGn",
        hover_name="artist_name",
        hover_data={"x_p": False, "y_p": False,
                    "new_cities": True, "revisit_cities": True,
                    "pct_revisit_cities": ":.1f", "total_events": True},
        text="artist_name" if lbl_sc else None,
        labels={
            "x_p": "New Cities",
            "y_p": "Revisit Cities"
        },
        title=f"Revisit vs. New Cities  |  n={len(df_s)}  |  min {min_ev} events",
        template="plotly_dark",
    )
    fig1.add_trace(go.Scatter(
        x=[0, max_diag], y=[0, max_diag],
        mode="lines", name="ratio = 1",
        line=dict(color="white", width=1, dash="dash"),
        hoverinfo="skip",
    ))
    fig1.update_traces(
        marker=dict(size=9, opacity=0.85, line=dict(width=0.5, color="white")),
        selector=dict(mode="markers")
    )
    if lbl_sc:
        fig1.update_traces(
            textposition="top center",
            textfont=dict(size=8, color="white"),
            selector=dict(mode="markers+text")
        )
    fig1.update_layout(
        height=510,
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        coloraxis_colorbar=dict(title=col_by.replace("_", " "))
    )
    with s2:
        st.plotly_chart(fig1, use_container_width=True)

    above = int((df_s["revisit_cities"] > df_s["new_cities"]).sum())
    below = int((df_s["revisit_cities"] < df_s["new_cities"]).sum())
    n = len(df_s)
    pct_above = above / n * 100
    pct_below = below / n * 100

    if pct_above > 50:
        pattern_text = (
            f"The majority of artists ({above} out of {n}, {pct_above:.0f}%) fall above the diagonal, "
            f"meaning they return to more cities than they visit for the first time. "
            f"This suggests a consolidation strategy — most artists in this selection tend to "
            f"play in proven markets rather than expanding into new locations."
        )
    elif pct_below > 50:
        pattern_text = (
            f"The majority of artists ({below} out of {n}, {pct_below:.0f}%) fall below the diagonal, "
            f"meaning they visit more new cities than they return to. "
            f"This points to a geographic expansion pattern — most artists prioritise "
            f"reaching new audiences in new locations over revisiting established ones."
        )
    else:
        pattern_text = (
            f"Artists are relatively evenly split across the diagonal ({above} above, {below} below, out of {n}). "
            f"There is no strong tendency toward either consolidation or geographic expansion "
            f"in this selection."
        )

    if col_by == "total_events":
        color_text = (
            "With events as the color dimension, check whether larger tours (brighter dots) "
            "cluster above or below the diagonal — this would indicate whether tour scale "
            "is linked to revisit behaviour."
        )
    elif col_by == "pct_revisit_cities":
        color_text = (
            "With revisit share as the color dimension, dots further above the diagonal "
            "should appear brighter, confirming that position relative to the line "
            "reflects the actual revisit percentage."
        )
    else:
        color_text = (
            "With listener count as the color dimension, any clustering of brighter dots "
            "on one side of the diagonal would suggest that audience size on Last.fm "
            "is related to how artists structure their tour geography."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>{pattern_text} {color_text}</p>
    </div>
    """, unsafe_allow_html=True)

else:
    with s2:
        st.warning("No data after filter.")

st.divider()
# ══════════════════════════════════════════════════════════════════════════
# GRAPH 2 — Box Plot Revisit-Rate nach Tour-Größe
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📦 Graph 2 — Revisit Rate by Tour Size</div>',
            unsafe_allow_html=True)

metric_descriptions = {
    "pct_revisit_cities": (
        "Artists are divided into equally sized groups based on their total number of tour events. "
        "The y-axis shows the <strong>share of revisit cities</strong> out of all cities visited. "
        "A value of 30% means 30% of the cities on a tour were places the artist had already played before. "
        "This focuses on geographic variety — how many distinct locations were new versus already known."
    ),
    "revisit_ratio": (
        "Artists are divided into equally sized groups based on their total number of tour events. "
        "The y-axis shows the <strong>ratio of revisit cities to new cities</strong>. "
        "A value of 1.0 means an artist visited exactly as many cities again as for the first time. "
        "Values above 1 indicate more revisits than new locations, values below 1 the opposite."
    ),
    "pct_events_revisit": (
        "Artists are divided into equally sized groups based on their total number of tour events. "
        "The y-axis shows the <strong>share of all events in revisit cities</strong>. "
        "This is typically higher than the city share — an artist playing 3 shows in the same city "
        "contributes 3 events but only 1 city. This captures how much touring activity "
        "is concentrated in already-familiar locations."
    ),
}

description_placeholder = st.empty()

b1, b2 = st.columns([1, 3])
with b1:
    n_grp = st.select_slider("Groups", [3, 4, 5], value=4, key="f4b_ng")
    y_met = st.radio(
        "Y-axis",
        ["pct_revisit_cities", "revisit_ratio", "pct_events_revisit"],
        index=0, key="f4b_y",
        format_func=lambda x: {
            "pct_revisit_cities": "% Revisit Cities",
            "revisit_ratio": "Ratio (Revisit / New)",
            "pct_events_revisit": "% Events in Revisit Cities"
        }[x]
    )

description_placeholder.markdown(
    metric_descriptions[y_met],
    unsafe_allow_html=True
)

df_bx = df_f4.dropna(subset=[y_met, "total_events"]).copy()
G_LBLS = {
    3: ["Small", "Medium", "Large"],
    4: ["Small", "Medium", "Large", "Very Large"],
    5: ["Mini", "Small", "Medium", "Large", "Very Large"]
}[n_grp]
G_COLORS = ["#2e86c1", "#1a9850", "#1DB954", "#52BE80", "#A9DFBF"]

try:
    df_bx["grp"] = pd.qcut(df_bx["total_events"], q=n_grp,
                           labels=G_LBLS, duplicates="drop")
    fig2 = go.Figure()
    for i, lbl in enumerate(G_LBLS):
        sub = df_bx[df_bx["grp"] == lbl]
        if len(sub) < 2:
            continue
        emin, emax = int(sub["total_events"].min()), int(sub["total_events"].max())
        fig2.add_trace(go.Box(
            y=sub[y_met],
            name=f"{lbl}<br><sub>{emin}–{emax} events  n={len(sub)}</sub>",
            marker_color=G_COLORS[i],
            line_color=G_COLORS[i],
            fillcolor=hex_rgba(G_COLORS[i]),
            boxpoints="outliers",
            marker=dict(size=5, opacity=0.7),
        ))

    y_labels = {
        "pct_revisit_cities": "% Revisit Cities",
        "revisit_ratio": "Ratio (Revisit / New)",
        "pct_events_revisit": "% Events in Revisit Cities"
    }
    fig2.update_layout(
        title=f"{y_labels[y_met]} by tour size",
        yaxis_title=y_labels[y_met],
        template="plotly_dark",
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"), height=430,
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        showlegend=False,
    )
    with b2:
        st.plotly_chart(fig2, use_container_width=True)

    meds = (
        df_bx.groupby("grp", observed=True)[y_met]
        .median()
        .reindex(G_LBLS)
        .tolist()
    )
    meds_clean = [m for m in meds if m is not None and not pd.isna(m)]
    med_diff = max(meds_clean) - min(meds_clean) if len(meds_clean) >= 2 else 0
    monotonic_up = all(meds_clean[i] <= meds_clean[i+1] for i in range(len(meds_clean)-1))
    monotonic_down = all(meds_clean[i] >= meds_clean[i+1] for i in range(len(meds_clean)-1))

    y_label_plain = y_labels[y_met]

    if med_diff < 3:
        interp_text = (
            f"The median {y_label_plain} remains similar across all tour size groups. "
            f"This suggests that revisit behaviour does not consistently depend on how large "
            f"the tour is — it appears to be more of an individual choice than a scale-driven pattern."
        )
    elif monotonic_up:
        interp_text = (
            f"The median {y_label_plain} increases from smaller to larger tour groups. "
            f"Artists with more events tend to show higher revisit rates, supporting the idea "
            f"that bigger tours increasingly rely on proven markets. "
            f"As tour scale grows, consolidation into familiar cities becomes more common."
        )
    elif monotonic_down:
        interp_text = (
            f"The median {y_label_plain} decreases from smaller to larger tour groups. "
            f"Artists with more events tend to visit a higher share of new cities rather than "
            f"returning to familiar ones. This could reflect that larger artists have the "
            f"resources and audience reach to expand into more locations."
        )
    else:
        interp_text = (
            f"The median {y_label_plain} varies across tour size groups without a clear "
            f"step-by-step pattern. This suggests that the relationship between tour scale "
            f"and revisit behaviour is not straightforward in this dataset."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>{interp_text}</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    with b2:
        st.warning(f"Error: {e}")

st.divider()
# ══════════════════════════════════════════════════════════════════════════
# GRAPH 3 — Meistbesuchte Städte (Balkendiagramm)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 3 — Most Visited Cities Across All Artists</div>',
            unsafe_allow_html=True)

description_placeholder = st.empty()

if city_df is not None:
    city_df["city"] = city_df["city"].str.strip()
    city_df["country"] = city_df["country"].str.strip()

    c1, c2 = st.columns([1, 3])
    with c1:
        top_n = st.slider("Top N Cities", 10, 40, 20, key="f4c_n")
        col_metric = st.radio(
            "Color by",
            ["Total Visits", "Number of Artists", "Capital city?"],
            index=0, key="f4c_col"
        )

    col_descriptions = {
        "Total Visits": (
            "This chart ranks cities by how often artists in the dataset performed there in total. "
            "The color intensity reflects visit count — darker bars indicate more visits. "
            "This shows which cities function as the central hubs of live music activity across all artists."
        ),
        "Number of Artists": (
            "The bars are ranked by total visits, but colored by how many distinct artists performed in each city. "
            "A city with many artists but fewer total visits suggests broad but shallow touring presence. "
            "A city with few artists but many visits suggests a small number of artists return there repeatedly."
        ),
        "Capital city?": (
            "Bars are colored by whether the city is a national capital or not. "
            "This makes it easy to see whether the most-visited touring destinations tend to be "
            "political and administrative centres, or whether economic and cultural hubs dominate instead."
        ),
    }

    description_placeholder.markdown(col_descriptions[col_metric])

    city_agg = (
        city_df.groupby(["city", "country"])
        .agg(
            total_visits=("visits", "sum"),
            n_artists=("artist_name", "nunique"),
            is_capital=("is_capital", "first")
        )
        .reset_index()
    )

    city_top = city_agg.nlargest(top_n, "total_visits").sort_values("total_visits")

    if col_metric == "Total Visits":
        fig3 = px.bar(
            city_top, x="total_visits", y="city", orientation="h",
            color="total_visits", color_continuous_scale="YlGn",
            hover_data={"city": False, "country": True, "total_visits": True,
                        "n_artists": True, "is_capital": True},
            labels={"total_visits": "Visits", "city": "", "n_artists": "Artists",
                    "country": "Country", "is_capital": "Capital"},
            template="plotly_dark"
        )
    elif col_metric == "Number of Artists":
        fig3 = px.bar(
            city_top, x="total_visits", y="city", orientation="h",
            color="n_artists", color_continuous_scale="Blues",
            hover_data={"city": False, "country": True, "total_visits": True,
                        "n_artists": True},
            labels={"total_visits": "Visits", "city": "", "n_artists": "Artists",
                    "country": "Country"},
            template="plotly_dark"
        )
    else:
        city_top["cap_label"] = city_top["is_capital"].apply(
            lambda x: "Capital city" if pd.notna(x) and int(x) == 1 else "Non-Capital city"
        )
        fig3 = px.bar(
            city_top, x="total_visits", y="city", orientation="h",
            color="cap_label",
            color_discrete_map={"Capital city": "#1DB954", "Non-Capital city": "#4a4a4a"},
            hover_data={"city": False, "country": True, "total_visits": True},
            labels={"total_visits": "Visits", "city": "", "cap_label": "Type",
                    "country": "Country"},
            template="plotly_dark"
        )

    fig3.update_layout(
        height=max(500, top_n * 32),
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333", title="Visits"),
        yaxis=dict(
            gridcolor="#333",
            tickfont=dict(size=12),
            automargin=True,
        ),
        margin=dict(l=120),
        title=f"Top {top_n} most visited cities",
    )
    with c2:
        st.plotly_chart(fig3, use_container_width=True)

    top_city = city_top.iloc[-1]["city"]
    top_visits = int(city_top.iloc[-1]["total_visits"])
    top_n_actual = len(city_top)
    top_n_check = city_agg.nlargest(top_n_actual, "total_visits")
    cap_n = int(top_n_check["is_capital"].sum())
    cap_threshold_high = top_n_actual * 0.6
    cap_threshold_mid = top_n_actual * 0.35

    if cap_n >= cap_threshold_high:
        capital_text = (
            f"{cap_n} of the top {top_n_actual} most-visited cities are national capitals. "
            "This suggests that touring strongly follows political and administrative centres — "
            "artists concentrate their performances in cities with high infrastructural visibility."
        )
    elif cap_n >= cap_threshold_mid:
        capital_text = (
            f"{cap_n} of the top {top_n_actual} most-visited cities are national capitals. "
            "Capitals are well represented, but major economic and cultural hubs play an equally "
            "important role — touring is not purely driven by political geography."
        )
    else:
        capital_text = (
            f"Only {cap_n} of the top {top_n_actual} most-visited cities are national capitals. "
            "Non-capital cities dominate — music and economic metros matter more than political centres "
            "when it comes to where artists choose to perform."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>
        The most visited city in this selection is <strong>{top_city}</strong> with {top_visits} total visits, 
        showing that touring is far from evenly spread across locations. A small number of cities 
        attract a disproportionate share of performances — these hubs represent established markets where 
        demand is already proven and artists are more likely to return.
        <br><br>
        {capital_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("⚠️ `f4_city_frequencies.csv` missing — please run `join_data.py`.")

st.divider()
# ══════════════════════════════════════════════════════════════════════════
# ZUSAMMENFASSUNG Q1
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Summary — Research Question 1: Revisit Cities</div>',
            unsafe_allow_html=True)

if global_pct > 50:
    pattern_text = (
        f"Across all artists in the dataset, {global_pct:.1f}% of all touring activity takes place "
        f"in cities that artists have visited before. This suggests that returning to proven markets "
        f"is the dominant touring strategy — artists tend to consolidate rather than expand geographically."
    )
elif global_pct > 25:
    pattern_text = (
        f"Across all artists in the dataset, {global_pct:.1f}% of all touring activity takes place "
        f"in cities that artists have visited before. Both geographic expansion and consolidation "
        f"play a role — artists balance between exploring new locations and returning to familiar ones."
    )
else:
    pattern_text = (
        f"Across all artists in the dataset, only {global_pct:.1f}% of all touring activity takes place "
        f"in cities that artists have visited before. Geographic expansion is clearly the dominant strategy — "
        f"most artists prioritise reaching new cities over returning to ones they already know."
    )

if global_ratio > 1:
    ratio_text = (
        f"With a global ratio of {global_ratio:.2f} revisit cities per new city, artists on average "
        f"return to more cities than they visit for the first time. "
        f"This points to a consolidation-first approach across the dataset."
    )
else:
    ratio_text = (
        f"With a global ratio of {global_ratio:.2f} revisit cities per new city, artists on average "
        f"visit far more new cities than they return to. "
        f"For every city an artist revisits, there are {1/global_ratio:.1f} new cities being added to the tour."
    )

st.markdown(f"""
<div class="insight-card">
    <h4>🎯 Answer to Research Question 1</h4>
    <p>
    {pattern_text}
    <br><br>
    {ratio_text} The average revisit rate of {mean_pct:.1f}% confirms this picture — 
    only about one in {round(100/mean_pct) if mean_pct > 0 else "many"} cities an artist plays 
    is a city they have been to before. This suggests that for most artists in this dataset, 
    touring is primarily a tool for geographic expansion rather than market consolidation.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="methodology-note">
    <p>
    <strong>Methodological note:</strong> A "Revisit City" is defined as a city where the Ticketmaster 
    dataset (2022–2026) records two or more events by the same artist. Cities are identified by name only, 
    not by venue. Events without a city name are excluded from the analysis.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()
st.markdown('<div id="geo-frage-2"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# RESEARCH QUESTION 2
# ══════════════════════════════════════════════════════════════════════════

# Load F6 data 
@st.cache_data
def load_f6_data():
    p1 = "data/processed/f6_capitals_visited.csv"
    p2 = "data/processed/f6_capitals_per_artist.csv"
    cap_gl = pd.read_csv(p1) if os.path.exists(p1) else None
    cap_ar = pd.read_csv(p2) if os.path.exists(p2) else None
    return cap_gl, cap_ar


cap_global, cap_per_artist = load_f6_data()

F6_COLS = ["capital_events", "non_capital_events", "pct_capital",
           "capital_ratio", "unique_capitals", "unique_non_capitals", "pct_capital_cities"]
f6_missing = [c for c in F6_COLS if c not in df.columns]

st.markdown("""
<div class="rq-box">
    <h3>🗺️ Research Question 2</h3>
    <p>What proportion of an artist's performances take place in capital cities
    compared to non-capital cities?</p>
</div>
""", unsafe_allow_html=True)

if f6_missing:
    st.error(f"⚠️ Missing data for Question 2: {f6_missing} — please re-run `join_data.py`.")
    st.stop()

st.markdown("""
**Definitions**

| Term | Meaning |
|------|---------|
| **Capital Event** | A concert held in a national capital city — for example, a show in Berlin, Paris, or Tokyo counts as a capital event, while a show in Hamburg or Lyon does not |
| **pct_capital** | Out of all concerts an artist played, what percentage were in capital cities? An artist with 10 shows, 3 of which were in capitals, has a pct_capital of 30% |
| **pct_capital_cities** | Out of all the cities an artist visited, what percentage were capitals? Each city counts only once — so an artist who played 5 shows in Berlin and 1 in Munich visited 2 cities, one of which is a capital: 50% |

**Why do both metrics exist?**
They can tell very different stories. An artist who plays 10 shows in London and 1 in Manchester
has a pct_capital of 91% — but only visited 2 cities, so pct_capital_cities is 50%.
pct_capital reflects how much of the actual touring activity happens in capitals.
pct_capital_cities reflects how broadly capitals feature in the tour routing.

**Hypothesis:** More popular artists perform proportionally more often in capital cities,
as capitals typically offer larger venues, greater media exposure, and a denser fan base.
""")

for c in F6_COLS:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df_f6 = df.dropna(subset=["capital_events", "non_capital_events"]).copy()

total_cap = df_f6["capital_events"].sum()
total_non = df_f6["non_capital_events"].sum()
total_all = total_cap + total_non
glob_pct = total_cap / total_all * 100 if total_all > 0 else 0
mean_pct = df_f6["pct_capital"].mean()
med_pct = df_f6["pct_capital"].median()

st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg. Capital Share", f"{mean_pct:.1f}%", delta=f"Median {med_pct:.1f}%")
k2.metric("Global Capital Share", f"{glob_pct:.1f}%")
k3.metric("Total Capital Events", f"{total_cap:.0f}")
k4.metric("Total Non-Capital Events", f"{total_non:.0f}")
st.divider()

# ══════════════════════════════════════════════════════════════════════════
# Q2 — GRAPH 1: Scatterplot pct_capital vs Listeners
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 1 — Capital City Share vs. Last.fm Listeners</div>',
            unsafe_allow_html=True)

metric_descriptions = {
    "pct_capital": (
        "Each dot represents one artist. The x-axis shows their Last.fm listener count (log scale), "
        "the y-axis shows what <strong>share of their total events</strong> took place in capital cities. "
        "The trend line shows whether artists with more listeners tend to play a larger or smaller "
        "proportion of their concerts in capitals."
    ),
    "pct_capital_cities": (
        "Each dot represents one artist. The x-axis shows their Last.fm listener count (log scale), "
        "the y-axis shows what <strong>share of the cities they visited</strong> are national capitals. "
        "Unlike the events metric, each city counts only once — this shows how capitals feature "
        "in an artist's tour routing independent of how many shows they played there."
    ),
}

description_placeholder = st.empty()

sc6_1, sc6_2 = st.columns([1, 3])
with sc6_1:
    sc6_y = st.radio(
        "Y-Axis",
        ["pct_capital", "pct_capital_cities"],
        index=0, key="f6s_y",
        format_func=lambda x: {
            "pct_capital": "% Capital Events",
            "pct_capital_cities": "% Capital Cities"
        }[x]
    )
    log_x_sc6 = st.checkbox("Log X (listeners)", value=True, key="f6s_logx")
    sc6_lbls = st.checkbox("Show Names", value=False, key="f6s_lbl")
    sc6_min = st.slider("Min. Events", 1, 20, 3, key="f6s_min")

description_placeholder.markdown(
    metric_descriptions[sc6_y],
    unsafe_allow_html=True
)

df_sc6 = df_f6[df_f6["total_events"] >= sc6_min].dropna(
    subset=[sc6_y, "listeners"]).copy()
df_sc6["listeners"] = pd.to_numeric(df_sc6["listeners"], errors="coerce")
df_sc6 = df_sc6.dropna(subset=["listeners"])

if len(df_sc6) >= 5:
    x_v = np.log10(df_sc6["listeners"] + 1) if log_x_sc6 else df_sc6["listeners"]
    y_v = df_sc6[sc6_y]

    df_sc6["x_plot"] = x_v.values
    df_sc6["y_plot"] = y_v.values

    y_lbl_map = {
        "pct_capital": "% Capital Events",
        "pct_capital_cities": "% Capital Cities"
    }
    x_label_sc6 = "log₁₀(Last.fm Listeners)" if log_x_sc6 else "Last.fm Listeners"

    # --- Trend line for the plot (uses the currently selected x scale) ---
    coef = np.polyfit(df_sc6["x_plot"], df_sc6["y_plot"], 1)
    x_line = np.linspace(df_sc6["x_plot"].min(), df_sc6["x_plot"].max(), 200)
    y_line = np.polyval(coef, x_line)

    # --- Slope for interpretation (always computed on log listeners so text stays stable) ---
    log_listeners = np.log10(df_sc6["listeners"] + 1)
    coef_interp = np.polyfit(log_listeners, df_sc6[sc6_y], 1)
    slope = coef_interp[0]

    fig_sc6 = px.scatter(
        df_sc6, x="x_plot", y="y_plot",
        hover_name="artist_name",
        hover_data={"x_plot": False, "y_plot": False,
                    "listeners": ":,", sc6_y: ":.1f", "total_events": True},
        color=sc6_y,
        color_continuous_scale="RdYlGn",
        text="artist_name" if sc6_lbls else None,
        labels={
            "x_plot": x_label_sc6,
            "y_plot": y_lbl_map[sc6_y]
        },
        title=f"{y_lbl_map[sc6_y]} vs. Last.fm Listeners  |  n = {len(df_sc6)}",
        template="plotly_dark",
    )
    fig_sc6.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode="lines", name="Trend line",
        line=dict(color="#1DB954", width=2.5),
        hoverinfo="skip",
    ))
    fig_sc6.update_traces(
        marker=dict(size=9, opacity=0.85, line=dict(width=0.5, color="white")),
        selector=dict(mode="markers")
    )
    if sc6_lbls:
        fig_sc6.update_traces(
            textposition="top center",
            textfont=dict(size=8, color="white"),
            selector=dict(mode="markers+text")
        )
    fig_sc6.update_layout(
        height=510, paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        coloraxis_showscale=False,
    )
    with sc6_2:
        st.plotly_chart(fig_sc6, use_container_width=True)

    y_label_plain = y_lbl_map[sc6_y]
    metric_plain = "events in capital cities" if sc6_y == "pct_capital" else "cities visited that are capitals"

    if abs(slope) < 0.5:
        interp_text = (
            f"The trend line is nearly flat, suggesting that Last.fm listener count has little "
            f"to no consistent relationship with the {y_label_plain.lower()}. "
            f"Artists across all popularity levels show a similar proportion of {metric_plain} — "
            f"touring decisions appear to be driven by other factors such as region, genre, or "
            f"venue availability rather than audience size."
        )
    elif slope > 0:
        interp_text = (
            f"The trend line slopes upward, suggesting that artists with more Last.fm listeners "
            f"tend to have a higher {y_label_plain.lower()}. "
            f"More popular artists appear to concentrate a greater share of their {metric_plain}, "
            f"which could reflect that larger artists benefit from the higher demand and bigger "
            f"venues that capital cities typically offer."
        )
    else:
        interp_text = (
            f"The trend line slopes downward, suggesting that artists with more Last.fm listeners "
            f"actually show a lower {y_label_plain.lower()}. "
            f"More popular artists appear to spread their performances more broadly — "
            f"a smaller share of their {metric_plain}, possibly because extensive touring "
            f"requires reaching beyond capitals into non-capital markets."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>{interp_text}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
# ══════════════════════════════════════════════════════════════════════════
# Q2 — GRAPH 2: Meistbesuchte Hauptstädte (global)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 2 — Most Visited Capital Cities Across All Artists</div>',
            unsafe_allow_html=True)

description_placeholder = st.empty()

if cap_global is not None and len(cap_global) > 0:
    cap_global_clean = cap_global.copy()
    cap_global_clean["city"] = cap_global_clean["city"].astype(str).str.strip().str.title()
    cap_global_clean["country"] = cap_global_clean["country"].astype(str).str.strip()
    cap_global_clean = cap_global_clean[
        (cap_global_clean["city"] != "") &
        (cap_global_clean["city"].str.lower() != "nan") &
        (cap_global_clean["city"].notna())
    ]
    cap_global_clean["total_visits"] = pd.to_numeric(cap_global_clean["total_visits"], errors="coerce")
    cap_global_clean["n_artists"] = pd.to_numeric(cap_global_clean["n_artists"], errors="coerce")
    cap_global_clean = cap_global_clean.dropna(subset=["total_visits", "city"])
    cap_global_clean = (
        cap_global_clean
        .groupby("city", as_index=False)
        .agg(
            total_visits=("total_visits", "sum"),
            n_artists=("n_artists", "sum"),
            country=("country", "first")
        )
    )

    h1, h2 = st.columns([1, 3])
    with h1:
        top_n_h = st.slider("Top N Capitals", 10, 30, 20, key="f6h_n")

    cap_top = cap_global_clean.nlargest(top_n_h, "total_visits").sort_values("total_visits")

    # Dynamic description based on current selection
    top1 = cap_top.iloc[-1]["city"]
    top1_visits = int(cap_top.iloc[-1]["total_visits"])
    top3 = cap_top.nlargest(3, "total_visits")["city"].tolist()
    most_diverse = cap_global_clean.nlargest(1, "n_artists").iloc[0]

    description_placeholder.markdown(
        f"This chart ranks the top {top_n_h} most visited capital cities by total artist visits across the dataset. "
        f"Each bar represents one capital — the longer the bar, the more performances took place there. "
        f"Currently the most visited capital is <strong>{top1}</strong> with {top1_visits} total visits.",
        unsafe_allow_html=True
    )

    fig_h = px.bar(
        cap_top,
        x="total_visits", y="city", orientation="h",
        color="total_visits",
        color_continuous_scale="YlGn",
        hover_data={"city": False, "country": True,
                    "total_visits": True, "n_artists": True},
        labels={"total_visits": "Total Visits", "city": ""},
        title=f"Top {top_n_h} most visited capital cities",
        template="plotly_dark",
    )
    fig_h.update_layout(
        height=max(500, top_n_h * 32),
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333"),
        yaxis=dict(
            gridcolor="#333",
            tickfont=dict(size=12),
            automargin=True,
        ),
        margin=dict(l=120),
        coloraxis_colorbar=dict(title="Visits"),
    )
    with h2:
        st.plotly_chart(fig_h, use_container_width=True)

    # Check if visits drop steeply after top 3
    visits_sorted = cap_top.sort_values("total_visits", ascending=False)["total_visits"].tolist()
    top3_avg = sum(visits_sorted[:3]) / 3 if len(visits_sorted) >= 3 else 0
    rest_avg = sum(visits_sorted[3:]) / len(visits_sorted[3:]) if len(visits_sorted) > 3 else 0
    steep_dropoff = top3_avg > rest_avg * 2 if rest_avg > 0 else False

    if steep_dropoff:
        pattern_text = (
            f"There is a steep drop-off after the top few cities — "
            f"{', '.join(top3)} stand far above the rest. "
            f"This suggests that artists do not visit capitals evenly but concentrate heavily "
            f"in a small number of commercially dominant music hubs."
        )
    else:
        pattern_text = (
            f"Visits are distributed relatively evenly across the top {top_n_h} capitals, "
            f"without a dramatic drop-off after the top cities. "
            f"This suggests that artists spread their capital city performances across a broader "
            f"range of destinations rather than concentrating in just a few hubs."
        )

    st.markdown(f"""
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>
        The most visited capital in this selection is <strong>{top1}</strong> with {top1_visits} total visits. 
        {most_diverse['city']} attracts the highest number of distinct artists 
        ({int(most_diverse['n_artists'])} artists, {int(most_diverse['total_visits'])} total visits).
        <br><br>
        {pattern_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("⚠️ `f6_capitals_visited.csv` not found — run `join_data.py`.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# Q2 — ARTIST DETAIL
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔍 Artist Detail — Capital City Profile</div>',
            unsafe_allow_html=True)
st.markdown("Which capital cities an artists has visited and how often?")

if cap_per_artist is not None:
    art_list6 = sorted(df_f6["artist_name"].dropna().unique().tolist())
    def_art6 = (df_f6.loc[df_f6["pct_capital"].idxmax(), "artist_name"]
                if len(df_f6) > 0 else art_list6[0])
    def_idx6 = art_list6.index(def_art6) if def_art6 in art_list6 else 0
    sel_art6 = st.selectbox("Artist", options=art_list6,
                            index=def_idx6, key="f6_detail")

    art_row6 = df_f6[df_f6["artist_name"] == sel_art6]
    art_caps = cap_per_artist[cap_per_artist["artist_name"] == sel_art6].sort_values(
        "visits", ascending=False)

    if len(art_row6) > 0:
        r6d = art_row6.iloc[0]
        d1, d2, d3, d4, d5 = st.columns(5)
        d1.metric("Total Events", int(r6d["total_events"]))
        d2.metric("Capital Events", int(r6d["capital_events"]))
        d3.metric("Non-Capital Events", int(r6d["non_capital_events"]))
        d4.metric("% Capital", f"{r6d['pct_capital']:.1f}%")
        d5.metric("Capitals visited", int(r6d["unique_capitals"]))

    if len(art_caps) > 0:
        fig_det6 = px.bar(
            art_caps, x="city", y="visits",
            hover_data={"city": True, "country": True, "visits": True},
            color="visits", color_continuous_scale="YlGn",
            labels={"visits": "Visits", "city": "Capital city"},
            title=f"{sel_art6} — Capital city visits",
            template="plotly_dark",
        )
        fig_det6.update_layout(
            height=350, paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#333", tickangle=-30),
            yaxis=dict(gridcolor="#333"),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_det6, use_container_width=True)
    else:
        st.info(f"{sel_art6} has no concerts in the dataset.")
else:
    st.info("⚠️  `f6_capitals_per_artist.csv` fehlt.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# ZUSAMMENFASSUNG Q2
# ══════════════════════════════════════════════════════════════════════════
mean_cap_pct = float(df_f6["pct_capital"].mean()) if "pct_capital" in df_f6.columns else 0.0
mean_cap_cities_pct = float(df_f6["pct_capital_cities"].mean()) if "pct_capital_cities" in df_f6.columns else 0.0

st.markdown('<div class="section-title">Summary — Research Question 2: Capital Cities</div>',
            unsafe_allow_html=True)

if mean_cap_pct > 50:
    overall_text = (
        f"On average, more than half of all artist performances in this dataset take place in capital cities "
        f"({mean_cap_pct:.1f}%). This suggests that capitals dominate live music activity — "
        f"artists strongly concentrate their touring in political and administrative centres."
    )
elif mean_cap_pct > 25:
    overall_text = (
        f"On average, {mean_cap_pct:.1f}% of all artist performances take place in capital cities. "
        f"Capitals play a significant but not dominant role — artists split their touring "
        f"between capital and non-capital cities, with non-capitals still accounting for the majority."
    )
else:
    overall_text = (
        f"On average, only {mean_cap_pct:.1f}% of all artist performances take place in capital cities. "
        f"Non-capital cities clearly dominate touring activity — artists perform the large majority "
        f"of their concerts outside of national capitals."
    )

st.markdown(f"""
<div class="insight-card">
    <h4>🎯 Answer to Research Question 2</h4>
    <p>
    {overall_text}
    <br><br>
    When looking at city routing rather than event counts, an average of 
    <strong>{mean_cap_cities_pct:.1f}%</strong> of the distinct cities artists visit are capitals. 
    This is {"higher" if mean_cap_cities_pct > mean_cap_pct else "lower"} than the event share, 
    which {"suggests that artists tend to play multiple shows in the same capital city" if mean_cap_cities_pct < mean_cap_pct 
    else "suggests that capitals are visited broadly but not necessarily revisited more than other cities"}.
    <br><br>
    Overall, this points to capitals being 
    {"a central pillar of tour planning" if mean_cap_pct > 40 
    else "an important but not exclusive part of tour routing" if mean_cap_pct > 20 
    else "one stop among many, with non-capital cities driving the majority of live activity"}.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="methodology-note">
    <p>
    <strong>Methodological note:</strong> A capital city is defined based on a pre-compiled list of 
    national capitals matched against Ticketmaster venue city names. Events without a city name 
    are excluded. The event share and city share may differ — the event share counts every 
    performance individually, while the city share counts each city only once per artist 
    regardless of how many shows were played there.
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# RESEARCH QUESTION 3
# ══════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div id="geo-frage-3"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="rq-box">
    <h3>🗺️ Research Question 3</h3>
    <p>How well do the countries where an artist has the highest <strong>listener reach</strong>
    on Last.fm align with the countries where they perform on their Ticketmaster tour?
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Definitions**

| Term | Meaning |
|------|---------|
| **Weighted Coverage** | The share of an artist's total Last.fm listener reach that is covered by their tour countries — the main metric of this analysis. An artist with 80% of their listeners in countries they tour in has a Weighted Coverage of 0.8 |
| **Streaming Reach** | The share of an artist's top streaming countries that are also visited on tour. A low value indicates untapped markets — countries with listeners but no live presence |

**Hypothesis:** Artists tend to perform in countries where their Last.fm listener counts are highest —
tour routing follows existing audience demand rather than exploring markets with no prior streaming presence.
""")

c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="insight-card">
        <h4>📡 Streaming Reach</h4>
        <p>Share of top streaming countries actually visited on tour.
        A low value indicates untapped markets — countries with listeners but no live presence.</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="insight-card accent">
        <h4>🗺️ Weighted Coverage</h4>
        <p>Listener-weighted share of streaming reach covered by the tour.
        Countries with more listeners contribute more to this score — the main metric of this analysis.</p>
    </div>""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_geo_align():
    p = "data/processed/geo_alignment.csv"
    if not os.path.exists(p):
        return None
    return pd.read_csv(p)

@st.cache_data
def load_geo_presence():
    p = "data/raw/lastfm_geo_presence.csv"
    if not os.path.exists(p):
        return None
    return pd.read_csv(p)

ga = load_geo_align()
geo = load_geo_presence()

if ga is None:
    st.error("Daten fehlen — Pipeline ausfuehren:")
    st.code("python scripts/collect_lastfm_geo.py\npython scripts/analyse_geo_align.py", language="bash")
    st.stop()

for c in ["jaccard", "tour_coverage", "streaming_reach", "listeners", "n_aligned",
          "n_streaming", "n_tour_countries"]:
    if c in ga.columns:
        ga[c] = pd.to_numeric(ga[c], errors="coerce")

# KPIs
n_artists = len(ga)
mean_tc = ga["tour_coverage"].mean()
mean_sr = ga["streaming_reach"].mean()
n_aligned_m = ga["n_aligned"].median()

st.divider()
mean_wc = ga["weighted_coverage"].mean() if "weighted_coverage" in ga.columns else mean_tc
k1, k2, k3, k4 = st.columns(4)
k1.metric("Artists", n_artists)
k2.metric("Ø Weighted Coverage", f"{mean_wc:.1%}", help="Listener-weighted share of reach covered by tour")
k3.metric("Ø Streaming Reach", f"{mean_sr:.1%}")
k4.metric("Median Aligned Countries", f"{int(n_aligned_m)}")
st.divider()
# ══════════════════════════════════════════════════════════════════════════
# GA2 — GRAPH 1: Scatterplot Listeners vs Jaccard
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 1 — Streaming Popularity vs. Geographic Alignment</div>',
            unsafe_allow_html=True)

description_placeholder = st.empty()

color_descriptions = {
    "n_tour_countries": (
        "Each dot is one artist. The x-axis shows their Last.fm listener count, the y-axis shows their "
        "<strong>geo-alignment score</strong> — how much of their global listener reach is covered by the countries they tour in. "
        "A score of 1.0 means the artist tours in every country where they have significant listeners; "
        "0.0 means none of those countries are visited on tour. "
        "Dots are colored by <strong>how many countries</strong> the artist toured in total — "
        "this helps spot whether artists who tour more broadly also align better with their listeners."
    ),
    "tour_coverage": (
        "Each dot is one artist. The x-axis shows their Last.fm listener count, the y-axis shows their "
        "<strong>geo-alignment score</strong> — how much of their global listener reach is covered by the countries they tour in. "
        "Dots are colored by <strong>tour coverage</strong> — the share of an artist's tour countries "
        "that are also among their top streaming countries. "
        "A high value means the artist mostly plays in countries where they already have a listener base."
    ),
    "streaming_reach": (
        "Each dot is one artist. The x-axis shows their Last.fm listener count, the y-axis shows their "
        "<strong>geo-alignment score</strong> — how much of their global listener reach is covered by the countries they tour in. "
        "Dots are colored by <strong>streaming reach</strong> — the share of an artist's top streaming countries "
        "that they actually visit on tour. "
        "A low value means many countries where the artist has listeners are never visited live."
    ),
}

g1a, g1b = st.columns([1, 3])
with g1a:
    color_by = st.selectbox(
        "Color by",
        ["n_tour_countries", "tour_coverage", "streaming_reach"],
        format_func=lambda x: {
            "n_tour_countries": "Tour Countries",
            "tour_coverage": "Tour Coverage",
            "streaming_reach": "Streaming Reach",
        }[x],
        key="ga2_color"
    )
    log_x_g1 = st.checkbox("Log X (listeners)", value=True, key="ga2_logx")
    show_labels_g1 = st.checkbox("Show Names", value=False, key="ga2_lbl")

description_placeholder.markdown(
    color_descriptions[color_by],
    unsafe_allow_html=True
)

GA2_Y = "weighted_coverage" if "weighted_coverage" in ga.columns else "jaccard"
GA2_Y_LABEL = "Geo-alignment score (listener-weighted)" if GA2_Y == "weighted_coverage" else "Jaccard Similarity"

df_g1 = ga.dropna(subset=["listeners", GA2_Y]).copy()

# x-axis toggle (log / linear)
if log_x_g1:
    df_g1["x_plot"] = np.log10(df_g1["listeners"] + 1)
    x_label_g1 = "log₁₀(Last.fm Listeners)"
else:
    df_g1["x_plot"] = df_g1["listeners"]
    x_label_g1 = "Last.fm Listeners"

# log version kept for stable interpretation
df_g1["log_listeners"] = np.log10(df_g1["listeners"] + 1)

# trend line follows the displayed x scale
coef_g1 = np.polyfit(df_g1["x_plot"], df_g1[GA2_Y], 1)
x_line_g1 = np.linspace(df_g1["x_plot"].min(), df_g1["x_plot"].max(), 200)
y_line_g1 = np.polyval(coef_g1, x_line_g1)

# slope for interpretation always based on log listeners
coef_interp_g1 = np.polyfit(df_g1["log_listeners"], df_g1[GA2_Y], 1)
slope_g1 = coef_interp_g1[0]

fig_g1 = px.scatter(
    df_g1, x="x_plot", y=GA2_Y,
    color=color_by,
    color_continuous_scale="Viridis",
    hover_name="artist_name",
    hover_data={
        "x_plot": False,
        "jaccard": ":.3f",
        "tour_coverage": ":.1%",
        "streaming_reach": ":.1%",
        "n_aligned": True,
        "n_tour_countries": True,
        "n_streaming": True,
    },
    text="artist_name" if show_labels_g1 else None,
    labels={
        "x_plot": x_label_g1,
        GA2_Y: GA2_Y_LABEL,
        "n_tour_countries": "Tour Countries",
    },
    title=f"Last.fm Listeners vs. Geo-alignment  |  n = {len(df_g1)}",
    template="plotly_dark",
)
fig_g1.add_trace(go.Scatter(
    x=x_line_g1, y=y_line_g1, mode="lines", name="Trend line",
    line=dict(color="#f59e0b", width=2.5), hoverinfo="skip",
))
if show_labels_g1:
    fig_g1.update_traces(
        textposition="top center",
        textfont=dict(size=7, color="white"),
        selector=dict(mode="markers+text")
    )
fig_g1.update_layout(
    height=480, paper_bgcolor="#080b14", plot_bgcolor="#161c2d",
    font=dict(color="white"),
    xaxis=dict(gridcolor="#232840"),
    yaxis=dict(gridcolor="#232840", range=[-0.05, 1.05], title=GA2_Y_LABEL),
    coloraxis_colorbar=dict(title=color_by.replace("_", " ").title()),
)
with g1b:
    st.plotly_chart(fig_g1, use_container_width=True)

if abs(slope_g1) < 0.05:
    interp_g1 = (
        "The trend line is nearly flat, suggesting that an artist's popularity on Last.fm "
        "does not consistently relate to how well their tour geography matches their listener footprint. "
        "Artists with large and small audiences show a similar spread of geo-alignment scores — "
        "how well an artist reaches their streaming audience through live shows appears to be "
        "an individual decision rather than something driven by overall popularity."
    )
elif slope_g1 > 0:
    interp_g1 = (
        "The trend line slopes upward, suggesting that more popular artists tend to have a higher "
        "geo-alignment score. As artists grow in popularity, their touring routes appear to follow "
        "where their listener demand is strongest — possibly because larger artists have more "
        "resources and data to plan tours around actual audience locations."
    )
else:
    interp_g1 = (
        "The trend line slopes downward, suggesting that despite having larger audiences, "
        "more popular artists actually cover a smaller share of their streaming markets through touring. "
        "As artists grow in popularity, their fanbase tends to spread into more countries than "
        "their tours can realistically reach — creating a growing gap between digital reach and live presence."
    )

st.markdown(f"""
<div class="insight-card">
    <h4>🔍 Interpretation</h4>
    <p>{interp_g1}</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GA2 — GRAPH 2: Top & Bottom Artists — Heatmap Streaming vs. Tour Countries
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 2 — Streaming Presence vs. Tour Countries per Artist</div>',
            unsafe_allow_html=True)

st.markdown("""
This chart displays the best or worst aligned artists in the dataset, 
showing three bars side by side for each artist:

- **Streaming Countries (purple)** — the number of countries where the artist appears in Last.fm's 
top artists list, meaning they have a significant listener presence there
- **Tour Countries (amber)** — the number of countries where the artist has at least one Ticketmaster event
- **Overlap (green)** — the number of countries that appear in both: countries where the artist 
both has listeners and actually performed

The more the green bar dominates relative to the purple and amber bars, the better aligned the artist is.
Use the selector on the left to switch between the best-aligned artists (those who tour closely where 
their fans are) and the worst-aligned artists (those with the largest gap between streaming presence 
and live touring). Artists are sorted by Streaming Reach — the share of their listener countries 
they actually visit on tour.
""")

g3a, g3b = st.columns([1, 3])
with g3a:
    n_show = st.slider("Number of Artists", 5, 20, 10, key="ga2_n")
    min_events = st.slider("Min. Future Events", 1, 20, 3, key="ga2_min")
    show_type = st.radio(
        "Show",
        ["Best Aligned", "Worst Aligned"],
        key="ga2_type"
    )

sort_col = "streaming_reach" if "streaming_reach" in ga.columns else "jaccard"

try:
    df_events = pd.read_csv("data/raw/ticketmaster_events.csv")
    df_events["event_date"] = pd.to_datetime(df_events["event_date"], errors="coerce")
    today = pd.Timestamp.today()

    future_events = df_events[df_events["event_date"] >= today]
    active_artists = (
        future_events.groupby("artist_name")
        .size()
        .reset_index(name="future_events")
    )
    active_artists = active_artists[
        active_artists["future_events"] >= min_events
    ]["artist_name"].tolist()

    ga_filtered = ga[ga["artist_name"].isin(active_artists)].copy()
    ga_filtered = ga_filtered[ga_filtered["n_tour_countries"] >= 3].copy()

except Exception:
    ga_filtered = ga.copy()

top_df = (
    ga_filtered.dropna(subset=["n_tour_countries", "n_streaming", "streaming_reach"])
    .nlargest(n_show, sort_col) if show_type == "Best Aligned"
    else ga_filtered.dropna(subset=["n_tour_countries", "n_streaming", "streaming_reach"])
    .nsmallest(n_show, sort_col)
)

fig_g3 = go.Figure()
fig_g3.add_trace(go.Bar(
    y=top_df["artist_name"],
    x=top_df["n_streaming"],
    name="Streaming Countries (Last.fm)",
    orientation="h",
    marker_color="#6366f1",
    hovertemplate="%{y}<br>Streaming: %{x} countries<extra></extra>",
))
fig_g3.add_trace(go.Bar(
    y=top_df["artist_name"],
    x=top_df["n_tour_countries"],
    name="Tour Countries (Ticketmaster)",
    orientation="h",
    marker_color="#f59e0b",
    hovertemplate="%{y}<br>Tour: %{x} countries<extra></extra>",
))
fig_g3.add_trace(go.Bar(
    y=top_df["artist_name"],
    x=top_df["n_aligned"],
    name="Overlap",
    orientation="h",
    marker_color="#10b981",
    hovertemplate="%{y}<br>Aligned: %{x} countries  Streaming Reach=%{customdata:.1%}<extra></extra>",
    customdata=top_df["streaming_reach"],
))

fig_g3.update_layout(
    title=f"{show_type} — Streaming vs. Tour Countries  |  min. {min_events} future events, min. 3 tour countries",
    barmode="group",
    xaxis_title="Number of Countries",
    template="plotly_dark",
    paper_bgcolor="#080b14",
    plot_bgcolor="#161c2d",
    font=dict(color="white"),
    height=max(420, n_show * 42),
    xaxis=dict(gridcolor="#232840"),
    yaxis=dict(gridcolor="#232840"),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,
        xanchor="center",
        x=0.5
    ),
    margin=dict(b=120)
)
with g3b:
    st.plotly_chart(fig_g3, use_container_width=True)

if show_type == "Best Aligned":
    interp_text = (
        "The artists shown here visit the highest share of the countries where they have Last.fm listeners. "
        "Their green overlap bar is large relative to the purple streaming bar — meaning most of the countries "
        "where they have an audience are also countries they perform in. "
        "For these artists, touring and streaming presence are closely aligned, "
        "suggesting their live schedule is built around where actual demand exists."
    )
else:
    interp_text = (
        "The artists shown here leave the largest share of their listener countries unreached by live performances. "
        "Two patterns are worth looking for: if the purple bar is much larger than the amber bar, "
        "the artist has a broad global listener base but only tours in a small fraction of those countries — "
        "their digital reach far exceeds their live presence. "
        "If the amber bar dominates instead, the artist tours extensively into countries where they have "
        "little existing listener presence — suggesting a strategy of building new audiences through "
        "live performance rather than serving existing ones."
    )

st.markdown(f"""
<div class="insight-card">
    <h4>🔍 Interpretation</h4>
    <p>{interp_text}</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# Summary Q3
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Summary — Research Question 3: Listener Reach vs. Tour Geography</div>',
            unsafe_allow_html=True)

mean_wc = ga["weighted_coverage"].mean() if "weighted_coverage" in ga.columns else np.nan
mean_sr = ga["streaming_reach"].mean() if "streaming_reach" in ga.columns else np.nan
mean_tc = ga["tour_coverage"].mean() if "tour_coverage" in ga.columns else np.nan
median_aligned = ga["n_aligned"].median() if "n_aligned" in ga.columns else np.nan

# ── Overall alignment text (based on mean_wc + slope_g1) ─────────────────
if mean_wc >= 0.6:
    if slope_g1 > 0.05:
        overall_text = (
            f"On average, artists cover <strong>{mean_wc:.1%}</strong> of their Last.fm listener reach "
            f"through the countries they tour in, indicating a strong overall alignment between "
            f"digital audience demand and live touring. The scatter plot reinforces this — "
            f"more popular artists show even stronger alignment, suggesting that tour routing "
            f"increasingly follows where demand is highest as artists grow."
        )
    elif abs(slope_g1) <= 0.05:
        overall_text = (
            f"On average, artists cover <strong>{mean_wc:.1%}</strong> of their Last.fm listener reach "
            f"through the countries they tour in, indicating a strong overall alignment between "
            f"digital audience demand and live touring. This holds consistently across all popularity "
            f"levels — the scatter plot shows no meaningful difference between larger and smaller artists."
        )
    else:
        overall_text = (
            f"On average, artists cover <strong>{mean_wc:.1%}</strong> of their Last.fm listener reach "
            f"through the countries they tour in, indicating a strong overall alignment. "
            f"Notably, the scatter plot suggests that more popular artists cover a slightly smaller share — "
            f"as global fanbases tend to grow faster than tour footprints, a widening gap between "
            f"digital reach and live presence emerges at higher popularity levels."
        )
elif mean_wc >= 0.3:
    if slope_g1 > 0.05:
        overall_text = (
            f"On average, artists cover <strong>{mean_wc:.1%}</strong> of their Last.fm listener reach "
            f"through the countries they tour in — a moderate level of alignment. "
            f"The scatter plot suggests this improves with popularity: more established artists appear "
            f"to route their tours more deliberately around where their listener demand is strongest."
        )
    elif abs(slope_g1) <= 0.05:
        overall_text = (
            f"On average, artists cover <strong>{mean_wc:.1%}</strong> of their Last.fm listener reach "
            f"through the countries they tour in, pointing to a moderate alignment between streaming "
            f"geography and live touring. The scatter plot shows no consistent relationship with "
            f"popularity — how well an artist reaches their streaming audience through live shows "
            f"appears to be an individual decision rather than something driven by audience size."
        )
    else:
        overall_text = (
            f"On average, artists cover <strong>{mean_wc:.1%}</strong> of their Last.fm listener reach "
            f"through the countries they tour in, pointing to only moderate alignment. "
            f"The scatter plot adds an important nuance: more popular artists actually show lower "
            f"alignment scores, suggesting that as fanbases spread globally, tours increasingly "
            f"fail to keep pace with the full geographic scope of listener demand."
        )
else:
    if slope_g1 > 0.05:
        overall_text = (
            f"On average, artists cover only <strong>{mean_wc:.1%}</strong> of their Last.fm listener reach "
            f"through the countries they tour in — indicating weak overall alignment. "
            f"The scatter plot does suggest some improvement at higher popularity levels, "
            f"but even the most popular artists in the dataset leave a large share of their "
            f"listener reach uncovered by live touring."
        )
    elif abs(slope_g1) <= 0.05:
        overall_text = (
            f"On average, artists cover only <strong>{mean_wc:.1%}</strong> of their Last.fm listener reach "
            f"through the countries they tour in, indicating weak alignment between streaming geography "
            f"and touring geography. The scatter plot confirms that this gap is consistent across "
            f"all popularity levels — neither large nor small artists consistently bridge the "
            f"distance between where they are heard and where they perform."
        )
    else:
        overall_text = (
            f"On average, artists cover only <strong>{mean_wc:.1%}</strong> of their Last.fm listener reach "
            f"through the countries they tour in, indicating weak alignment between streaming geography "
            f"and touring geography. The scatter plot makes this even more pronounced: more popular "
            f"artists show lower alignment scores, as their global fanbases grow into far more "
            f"countries than their tours can realistically reach."
        )

# ── Streaming reach + Graph 2 pattern ────────────────────────────────────
if "streaming_reach" in ga.columns and "n_tour_countries" in ga.columns:
    best_artists = ga.nlargest(5, "streaming_reach")
    worst_artists = ga.nsmallest(5, "streaming_reach")
    best_avg_tour = best_artists["n_tour_countries"].mean()
    worst_avg_tour = worst_artists["n_tour_countries"].mean()

    if mean_sr >= 0.5:
        sr_base = (
            f"With an average Streaming Reach of <strong>{mean_sr:.1%}</strong>, "
            f"artists typically visit at least half of their strongest listener markets on tour."
        )
    elif mean_sr >= 0.2:
        sr_base = (
            f"The average Streaming Reach of <strong>{mean_sr:.1%}</strong> means that artists "
            f"visit only a minority of their strongest streaming countries live, "
            f"pointing to noticeable untapped markets."
        )
    else:
        sr_base = (
            f"With an average Streaming Reach of only <strong>{mean_sr:.1%}</strong>, "
            f"most top streaming countries remain unvisited on tour — "
            f"indicating a large gap between where artists are heard and where they actually perform."
        )

    if best_avg_tour > worst_avg_tour * 1.5:
        graph2_text = (
            f"{sr_base} The artist comparison in Graph 2 shows that the best-aligned artists "
            f"tend to tour in more countries overall, which naturally increases the chance of "
            f"reaching their listener base. The worst-aligned artists consistently show a broad "
            f"streaming presence with a far smaller tour footprint — their digital reach "
            f"clearly outpaces their live activity."
        )
    elif worst_avg_tour > best_avg_tour * 1.5:
        graph2_text = (
            f"{sr_base} Interestingly, Graph 2 shows that the worst-aligned artists often tour "
            f"in just as many — or more — countries than the best-aligned group. Their misalignment "
            f"is not due to touring too little, but to routing into countries where their listener "
            f"presence is weak, suggesting a strategy of building new audiences rather than "
            f"serving existing ones."
        )
    else:
        graph2_text = (
            f"{sr_base} Graph 2 shows that the gap between best- and worst-aligned artists is "
            f"not simply a matter of tour size — both groups visit a comparable number of countries. "
            f"What sets them apart is whether those countries overlap with their actual listener base: "
            f"the best-aligned artists have a large overlap between streaming presence and tour routing, "
            f"while the worst-aligned leave many of their strongest listener countries unvisited."
        )
else:
    graph2_text = (
        f"With an average Streaming Reach of <strong>{mean_sr:.1%}</strong>, "
        f"a relevant share of listener countries remains unreached by live touring."
    )

st.markdown(f"""
<div class="insight-card">
    <h4>🎯 Answer to Research Question 3</h4>
    <p>
    {overall_text}
    <br><br>
    {graph2_text}
    <br><br>
    The median artist aligns across 
    <strong>{int(median_aligned) if pd.notna(median_aligned) else 0}</strong> countries 
    between their streaming hotspots and tour destinations. Overall, this suggests that touring is 
    <strong>{"strongly" if mean_wc >= 0.6 else "partly" if mean_wc >= 0.3 else "weakly"}</strong> 
    aligned with country-level listener reach — but for most artists, a relevant share of their 
    digital audience remains unreached by live performance.
    </p>
</div>
""", unsafe_allow_html=True)
