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
        "The y-axis shows the <strong>share of revisit cities</strong> out of all cities visited. "
        "A value of 30% means 30% of the cities on a tour were places the artist had already played before. "
        "This focuses on geographic variety — how many distinct locations were new versus already known."
    ),
    "revisit_ratio": (
        "The y-axis shows the <strong>ratio of revisit cities to new cities</strong>. "
        "A value of 1.0 means an artist visited exactly as many cities again as for the first time. "
        "Values above 1 indicate more revisits than new locations, values below 1 the opposite."
    ),
    "pct_events_revisit": (
        "The y-axis shows the <strong>share of all events in revisit cities</strong>. "
        "This is typically higher than the city share — an artist playing 3 shows in the same city "
        "contributes 3 events but only 1 city. This captures how much touring activity "
        "is concentrated in already-familiar locations."
    ),
}

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

# Description text between title and chart — rendered after controls are read
st.markdown(
    f"Artists are divided into equally sized groups based on their total number of tour events — "
    f"from small to very large. {metric_descriptions[y_met]}",
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

st.markdown("""
This horizontal bar chart ranks cities by their total number of artist visits across the entire dataset, showing which cities function as the central hubs of live music activity. The colour encoding can be switched to show the number of distinct artists who performed there, or to highlight which cities are national capitals. A minimum artist threshold filters out cities that only appear in a single artist's data, ensuring the results reflect genuinely shared touring destinations.
""")

if city_df is not None:
    # Fix Problem 2: Leerzeichen entfernen vor dem Gruppieren
    city_df["city"] = city_df["city"].str.strip()
    city_df["country"] = city_df["country"].str.strip()

    c1, c2 = st.columns([1, 3])
    with c1:
        top_n = st.slider("Top N Cities", 10, 40, 20, key="f4c_n")
        col_metric = st.radio("Color by",
                              ["Total Visits", "Number of Artists", "Capital city?"],
                              index=0, key="f4c_col")
        min_art = st.slider("Minimum Artists", 1, 10, 2, key="f4c_ma")

    city_agg = (
        city_df.groupby(["city", "country"])
        .agg(total_visits=("visits", "sum"),
             n_artists=("artist_name", "nunique"),
             is_capital=("is_capital", "first"))
        .reset_index()
    )
    city_agg = city_agg[city_agg["n_artists"] >= min_art]
    city_top = city_agg.nlargest(top_n, "total_visits").sort_values("total_visits")

    if col_metric == "Total Visits":
        fig3 = px.bar(city_top, x="total_visits", y="city", orientation="h",
                      color="total_visits", color_continuous_scale="YlGn",
                      hover_data={"city": False, "country": True, "total_visits": True,
                                  "n_artists": True, "is_capital": True},
                      labels={"total_visits": "Visits", "city": "", "n_artists": "Artists",
                              "country": "Country", "is_capital": "Capital"},
                      template="plotly_dark")
    elif col_metric == "Number of Artists":
        fig3 = px.bar(city_top, x="total_visits", y="city", orientation="h",
                      color="n_artists", color_continuous_scale="Blues",
                      hover_data={"city": False, "country": True, "total_visits": True,
                                  "n_artists": True},
                      labels={"total_visits": "Visits", "city": "", "n_artists": "Artists",
                              "country": "Country"},
                      template="plotly_dark")
    else:
        city_top["cap_label"] = city_top["is_capital"].apply(
            lambda x: "Capital city" if pd.notna(x) and int(x) == 1 else "Non-Capital city"
        )
        fig3 = px.bar(city_top, x="total_visits", y="city", orientation="h",
                      color="cap_label",
                      color_discrete_map={"Capital city": "#1DB954", "Non-Capital city": "#4a4a4a"},
                      hover_data={"city": False, "country": True, "total_visits": True},
                      labels={"total_visits": "Visits", "city": "", "cap_label": "Type",
                              "country": "Country"},
                      template="plotly_dark")

    fig3.update_layout(
        height=max(360, top_n * 22),
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333", title="Visits"),
        yaxis=dict(gridcolor="#333"),
        title=f"Top {top_n} most visited cities (min. {min_art} Artists)",
    )
    with c2:
        st.plotly_chart(fig3, use_container_width=True)

    top20 = city_agg.nlargest(20, "total_visits")
    cap20 = int(top20["is_capital"].sum())

    st.markdown(f"""
    <div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
    <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
    <div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;">
    <strong>{cap20} of the top 20 most-visited cities ({cap20 / 20 * 100:.0f}%)</strong> are capital cities.
    {"Capitals clearly dominate — touring follows political and administrative centres." if cap20 >= 12
    else "Capitals are over-represented, but major economic centres play an equally important role." if cap20 >= 7
    else "Non-capitals dominate — music metros and economic hubs matter more than political capitals."}
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
    <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
    <div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;">
    A strong concentration of visits in only a few top cities shows that touring is not evenly spread across locations. Instead, many artists perform in the same well-known hubs. These hubs represent established markets where artists already know there is strong demand, which makes them more likely to return there again.
    </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("⚠️  `f4_city_frequencies.csv` fehlt — `join_data.py` ausführen.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# ZUSAMMENFASSUNG Q1
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Summary — Research Question 1: Revisit Cities</div>',
            unsafe_allow_html=True)

corr_tmp = df_f4.dropna(subset=["pct_revisit_cities", "total_events"])
r_s, p_s = stats.pearsonr(corr_tmp["pct_revisit_cities"], corr_tmp["total_events"])
r2_s = r_s ** 2

st.markdown(f"""
| Metric | Value |
|--------|------|
| Analysed Artists | {len(df_f4)} |
| Ø Revisit-Rate (% Cities) | {mean_pct:.1f}% |
| Median Revisit-Rate | {median_pct:.1f}% |
| Global Ratio (revisit / new) | {global_ratio:.3f} |
| % of all Tourings = Revisit | {global_pct:.1f}% |
| Pearson r (% Revisit vs. Events) | {r_s:.3f} |
| R² | {r2_s:.1%} |
| p-Value | {p_s:.4f} |
| Signifikant | {'Yes' if p_s < 0.05 else 'No'} |
""")

st.markdown(f"""
<div class="insight-card">
    <h4>🎯 Summary — Research Question 1: Revisit Cities</h4>
    <p>
    On average, 15.2% of the cities artists visit are revisit cities. This means that artists return to only about one out of seven cities they have already played in.
    The global ratio of 0.16 supports this pattern: for every new city an artist visits, there are only 0.16 cities that they revisit. This shows that geographic expansion is the main touring strategy, meaning that artists usually prefer to perform in new cities rather than returning to the same ones.
    <br><br>
    However, there is a positive relationship between tour size and the revisit rate (r = 0.212). This suggests that larger artists are more likely to return to cities where they have already performed successfully. In other words, the bigger the tour, the stronger the tendency to revisit known markets, while smaller artists explore more new cities.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="methodology-note">
    <p>
    <strong>Methodological Note:</strong>
    A “Revisit City” is defined as a city where the Ticketmaster dataset (2022–2026) records two or more events by the same artist. Cities are identified by city name only, not by venue. 
    If an artist performs multiple concerts in the same city on the same day, these are counted as separate events. Events without a city name are excluded from the analysis.
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
    st.error(f"⚠️  Daten für Frage 2 fehlen: {f6_missing} — `join_data.py` erneut ausführen.")
    st.stop()

st.markdown("""
**Definitions**

| Term | Meaning |
|---------|-----------|
| **Capital Event** | Concert in a capital city (classified using the RestCountries API) |
| **pct_capital** | Capital Events / Total Events × 100 - measures the share of the total concert volume |
| **pct_capital_cities** | Unique capital cities / all unique cities × 100 — measures geographic breadth |
| **capital_ratio** | Capital Events / Non-Capital Events - indicates how many non-capital shows occur per capital show |
| **unique_capitals** | Number of different capital cities an artist visits |

**Why two metrics (pct_capital vs. pct_capital_cities)?**
An artist who performs three times in Berlin and once in Munich has
pct_capital = 75% but pct_capital_cities = 50%.
Both perspectives are relevant - one reflects performance volume, while the other captures geographic strategy.

**Hypothesis**: More popular artists (with a higher number of listeners) perform proportionally more often in capital cities, as capitals typically offer larger venues, greater media exposure, and a denser fan base.
""")

# Daten vorbereiten
for c in F6_COLS:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df_f6 = df.dropna(subset=["capital_events", "non_capital_events"]).copy()

# Globale Kennzahlen
total_cap = df_f6["capital_events"].sum()
total_non = df_f6["non_capital_events"].sum()
total_all = total_cap + total_non
glob_pct = total_cap / total_all * 100 if total_all > 0 else 0
glob_ratio = total_cap / total_non if total_non > 0 else 0
mean_pct = df_f6["pct_capital"].mean()
med_pct = df_f6["pct_capital"].median()

st.divider()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Ø pct_capital", f"{mean_pct:.1f}%", delta=f"Median {med_pct:.1f}%")
k2.metric("Global Capital-Anteil", f"{glob_pct:.1f}%")
k3.metric("Capital Events gesamt", f"{total_cap:.0f}")
k4.metric("Non-Capital Events", f"{total_non:.0f}")
k5.metric("Ratio Capital / Non-Capital", f"{glob_ratio:.3f}")
st.divider()

# ══════════════════════════════════════════════════════════════════════════
# Q2 — GRAPH 1: Balkendiagramm pct_capital nach Listeners-Gruppe
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 1 — Average share of Capital City Performances by Popularity Tier</div>',
            unsafe_allow_html=True)

st.markdown("""
Artists are grouped into popularity tiers based on their number of Last.fm listeners or tour size. The bar chart shows the average share of performances taking place in capital cities for each group.
If more popular artists consistently played a larger share of concerts in capital cities, we would expect the bars to increase from left to right. However, the pattern appears relatively mixed, suggesting that artist popularity may not strongly determine whether performances take place in capital cities or non-capital cities
""")

g1, g2 = st.columns([1, 3])
with g1:
    n_tiers_f6 = st.select_slider("Number of Tiers", [3, 4, 5], value=4, key="f6b_nt")
    bar_metric = st.radio("Metric",
                          ["pct_capital", "pct_capital_cities", "unique_capitals"],
                          index=0, key="f6b_m",
                          format_func=lambda x: {
                              "pct_capital": "% Capital Events",
                              "pct_capital_cities": "% Capital Cities",
                              "unique_capitals": "Ø Visited Capital Cities"}[x])
    groupby_col = st.radio("Group by",
                           ["listeners", "total_events"],
                           index=0, key="f6b_gc",
                           format_func=lambda x: {"listeners": "Listeners", "total_events": "Tour-Scale"}[x])

df_b6 = df_f6.dropna(subset=[bar_metric, groupby_col]).copy()
df_b6[groupby_col] = pd.to_numeric(df_b6[groupby_col], errors="coerce")
df_b6 = df_b6.dropna(subset=[groupby_col])

g_lbls_f6 = {
    3: ["Low", "Middle", "High"],
    4: ["Q1 Low", "Q2 Low-mid", "Q3 Mid-high", "Q4 High"],
    5: ["Q1 Low", "Q2 Low-mid", "Q3 Mid", "Q4 Mid-high", "Q5 High"],
}[n_tiers_f6]
G_COLORS_F6 = ["#4a4a4a", "#7fb3d3", "#1a9850", "#1DB954", "#52BE80"][:n_tiers_f6]

try:
    df_b6["tier"] = pd.qcut(df_b6[groupby_col], q=n_tiers_f6,
                            labels=g_lbls_f6, duplicates="drop")
    grp6 = df_b6.groupby("tier", observed=True)[bar_metric].agg(["mean", "median", "count"]).reset_index()
    grp6.columns = ["tier", "mean", "median", "n"]

    fig_b6 = go.Figure()
    fig_b6.add_trace(go.Bar(
        x=grp6["tier"].astype(str),
        y=grp6["mean"],
        marker=dict(color=G_COLORS_F6),
        text=[f"{v:.1f}" for v in grp6["mean"]],
        textposition="outside",
        textfont=dict(color="white", size=13, family="monospace"),
        customdata=grp6[["median", "n"]].values,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Mean: %{y:.1f}<br>"
            "Median: %{customdata[0]:.1f}<br>"
            "n Artists: %{customdata[1]}<extra></extra>"
        )
    ))
    y_label_map = {"pct_capital": "Ø % Capital Events",
                   "pct_capital_cities": "Ø % Capital Cities",
                   "unique_capitals": "Ø Visited Capital Cities"}
    fig_b6.update_layout(
        title=f"{y_label_map[bar_metric]} by {groupby_col.replace('_', ' ').title()}-Tier",
        yaxis_title=y_label_map[bar_metric],
        xaxis_title=f"{groupby_col.replace('_', ' ').title()}-Group",
        template="plotly_dark",
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"), height=400,
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        showlegend=False,
    )
    with g2:
        st.plotly_chart(fig_b6, use_container_width=True)

    # Kruskal-Wallis
    kw_arr = [df_b6[df_b6["tier"] == g][bar_metric].dropna().values
              for g in g_lbls_f6 if len(df_b6[df_b6["tier"] == g]) > 1]
    if len(kw_arr) >= 2:
        kw_h, kw_p = stats.kruskal(*kw_arr)
        m_lo = float(grp6["mean"].iloc[0])
        m_hi = float(grp6["mean"].iloc[-1])
        st.markdown(f"""
        <div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
        <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
        <div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;">
        Kruskal-Wallis H = <strong>{kw_h:.2f}</strong>, p = <strong>{kw_p:.4f}</strong>
        → <strong>{"Significant" if kw_p < 0.05 else "Not significant"}</strong>.
        {y_label_map[bar_metric]}: lowest tier = <strong>{m_lo:.1f}</strong> → highest tier = <strong style="color:#1DB954">{m_hi:.1f}</strong> (Δ = {m_hi - m_lo:+.1f}).
        The Kruskal–Wallis test examines whether the selected metric differs across the popularity tiers. A p-value above 0.05 indicates that the observed differences between the groups are not statistically significant.
        The average metric values remain relatively similar across tiers, with the lowest tier at {m_lo:.1f} and the highest tier at {m_hi:.1f} (Δ = {m_hi - m_lo:+.1f}). This small difference suggests that popularity does not meaningfully influence this touring pattern.
        Overall, the results indicate that capital city preference is not strongly driven by audience size, and other factors such as tour logistics, venue availability, or regional demand may play a larger role.
        </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
        <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
        <div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;">
        The results indicate that there is no meaningful difference across popularity tiers in the selected metric. The average values remain relatively similar between the lowest and highest tiers, suggesting that artist popularity does not strongly influence whether performances take place in capital cities or non-capital cities.
        Overall, this implies that capital city preference is not primarily driven by audience size. Instead, other factors—such as venue availability, touring logistics, regional demand, or booking strategies-are likely to play a more important role in determining where artists perform.
        </div>
        </div>
        """, unsafe_allow_html=True)
except Exception as e:
    with g2:
        st.warning(f"Error: {e}")

st.divider()
# ══════════════════════════════════════════════════════════════════════════
# Q2 — GRAPH 2: Scatterplot pct_capital vs Listeners
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 2 — Capital City Share vs. Last.fm Listener Popularity</div>',
            unsafe_allow_html=True)

st.markdown("""
This scatterplot examines the continuous relationship between an artist's streaming popularity and the proportion of their concerts held in capital cities. The x-axis shows Last.fm listener counts on a log scale to compress the wide range of popularity values, while the y-axis shows the selected capital-city metric. A green OLS regression line is overlaid to capture the overall trend across all artists, and each dot can be hovered to inspect individual cases.
""")

sc6_1, sc6_2 = st.columns([1, 3])
with sc6_1:
    sc6_y = st.radio("X-Axis",
                     ["pct_capital", "pct_capital_cities"],
                     index=0, key="f6s_y",
                     format_func=lambda x: {"pct_capital": "% Capital Events",
                                            "pct_capital_cities": "% Capital Cities"}[x])
    sc6_logy = st.checkbox("Log Y-Axis", value=False, key="f6s_logy")
    sc6_lbls = st.checkbox("Show Names", value=False, key="f6s_lbl")
    sc6_min = st.slider("Min-Events", 1, 20, 3, key="f6s_min")

df_sc6 = df_f6[df_f6["total_events"] >= sc6_min].dropna(
    subset=[sc6_y, "listeners"]).copy()
df_sc6["listeners"] = pd.to_numeric(df_sc6["listeners"], errors="coerce")
df_sc6 = df_sc6.dropna(subset=["listeners"])

if len(df_sc6) >= 5:
    x_v = np.log10(df_sc6["listeners"] + 1)
    y_v = np.log10(df_sc6[sc6_y] + 1) if sc6_logy else df_sc6[sc6_y]
    r6, p6 = stats.pearsonr(x_v, y_v)
    r2_6 = r6 ** 2

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("n Artists", len(df_sc6))
    m2.metric("Pearson r", f"{r6:.3f}")
    m3.metric("R²", f"{r2_6:.1%}")
    m4.metric("p-Wert", f"{p6:.4f}",
              delta="signifikant" if p6 < 0.05 else "not signifikant",
              delta_color="normal" if p6 < 0.05 else "inverse")

    df_sc6["x_plot"] = x_v.values
    df_sc6["y_plot"] = y_v.values

    y_lbl_map = {"pct_capital": "% Capital Events", "pct_capital_cities": "% Capital Cities"}

    coef = np.polyfit(df_sc6["x_plot"], df_sc6["y_plot"], 1)
    x_line = np.linspace(df_sc6["x_plot"].min(), df_sc6["x_plot"].max(), 200)
    y_line = np.polyval(coef, x_line)

    fig_sc6 = px.scatter(
        df_sc6, x="x_plot", y="y_plot",
        hover_name="artist_name",
        hover_data={"x_plot": False, "y_plot": False,
                    "listeners": ":,", sc6_y: ":.1f", "total_events": True},
        color="pct_capital",
        color_continuous_scale="RdYlGn",
        text="artist_name" if sc6_lbls else None,
        labels={"x_plot": "log₁₀(Last.fm Listeners)",
                "y_plot": ("log₁₀(" if sc6_logy else "") + y_lbl_map[sc6_y] + (")" if sc6_logy else "")},
        title=f"{y_lbl_map[sc6_y]} vs. Last.fm Listeners  |  r = {r6:.3f}  |  n = {len(df_sc6)}",
        template="plotly_dark",
    )
    fig_sc6.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode="lines", name="OLS",
        line=dict(color="#1DB954", width=2.5),
        hoverinfo="skip",
    ))
    fig_sc6.update_traces(marker=dict(size=9, opacity=0.85,
                                      line=dict(width=0.5, color="white")),
                          selector=dict(mode="markers"))
    if sc6_lbls:
        fig_sc6.update_traces(textposition="top center",
                              textfont=dict(size=8, color="white"),
                              selector=dict(mode="markers+text"))
    fig_sc6.update_layout(
        height=510, paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        coloraxis_showscale=False,
    )
    with sc6_2:
        st.plotly_chart(fig_sc6, use_container_width=True)

    strength = "strong" if abs(r6) >= 0.7 else "moderate" if abs(r6) >= 0.4 else "weak"

    st.markdown(f"""
    <div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
    <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
    <div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;">
    Pearson r = <strong>{r6:.3f}</strong>, R² = <strong>{r2_6:.1%}</strong>, p = <strong>{p6:.4f}</strong>
    → <strong>{strength} {"positive" if r6 > 0 else "negative"} correlation</strong>,
    {"statistically significant" if p6 < 0.05 else "not statistically significant"}.
    Pearson r measures the strength and direction of the relationship between streaming popularity and capital-city share — a value near 0 indicates virtually no linear relationship.
    R² = <strong>{r2_6:.1%}</strong> means that listener popularity explains only {r2_6:.1%} of the variance in capital-city share; the remaining {100 - r2_6*100:.1f}% is driven by other factors such as genre, touring region, or booking strategy.
    {"A p-value of " + f"{p6:.4f}" + " confirms this result is statistically significant — the relationship is unlikely to be a random artefact." if p6 < 0.05 else "A p-value of " + f"{p6:.4f}" + " means this result is not statistically significant — the observed correlation could easily be due to chance in a sample of this size."}
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
    <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
    <div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;">
    {"More popular artists play proportionally more shows in capitals — larger venues and stronger media presence in capitals make them attractive targets. This supports the hypothesis in Research Question 2." if r6 > 0.2 and p6 < 0.05
    else "More popular artists actually show a lower capital share — extensive touring requires going beyond capitals into non-capital markets. This challenges the hypothesis in Research Question 2." if r6 < -0.2 and p6 < 0.05
    else "Listener popularity is not a meaningful predictor of capital-city share — touring decisions in Research Question 2 appear driven by other factors such as region, genre, or booking strategy."}
    </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# Q2 — GRAPH 3: Meistbesuchte Hauptstädte (global)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 3 — Most Visited Capital Cities Across All Artists</div>',
            unsafe_allow_html=True)

st.markdown("""
This chart ranks capital cities by the total number of artist visits across all artists in the dataset.
Each bar represents one capital city — the longer the bar, the more artists performed there.
Look for whether the ranking is dominated by a few mega-hubs or distributed more evenly across many capitals.
""")

if cap_global is not None and len(cap_global) > 0:

    # Clean up data
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

    # Merge duplicates
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

    fig_h = px.bar(
        cap_top,
        x="total_visits", y="city", orientation="h",
        color="total_visits",
        color_continuous_scale="YlGn",
        hover_data={"city": False, "country": True,
                    "total_visits": True, "n_artists": True},
        labels={"total_visits": "Total Visits", "city": ""},
        title=f"Top {top_n_h} Most Visited Capital Cities",
        template="plotly_dark",
    )
    fig_h.update_layout(
        height=max(340, top_n_h * 22),
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#333"), yaxis=dict(gridcolor="#333"),
        coloraxis_colorbar=dict(title="Visits"),
    )
    with h2:
        st.plotly_chart(fig_h, use_container_width=True)

    top3 = cap_top.nlargest(3, "total_visits")["city"].tolist()
    most_diverse = cap_global_clean.nlargest(1, "n_artists").iloc[0]

    st.markdown(f"""
    <div style="background:#0f1829;border:1px solid #1e2d45;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
    <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
    <div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;">
    The top 3 most-visited capital cities are <strong style="color:#1DB954">{", ".join(top3)}</strong>, 
    with {most_diverse['city']} attracting the most distinct artists ({int(most_diverse['n_artists'])} artists, {int(most_diverse['total_visits'])} total visits).
    The steep drop-off after the top 3–5 cities shows that artists are not drawn to capitals in general — 
    they concentrate in a few commercially dominant music hubs.
    </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("⚠️  `f6_capitals_visited.csv` not found — run `join_data.py`.")

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
st.markdown('<div class="section-title">Summary — Question 2: Capital Cities</div>',
            unsafe_allow_html=True)

corr6 = df_f6.dropna(subset=["pct_capital", "listeners"]).copy()
corr6["listeners"] = pd.to_numeric(corr6["listeners"], errors="coerce")
corr6 = corr6.dropna(subset=["listeners"])
r6_s = p6_s = None
if len(corr6) >= 5:
    r6_s, p6_s = stats.pearsonr(np.log10(corr6["listeners"] + 1), corr6["pct_capital"])

r6_str = f"{r6_s:.3f}" if r6_s is not None else "n/a"
p6_str = f"{p6_s:.4f}" if p6_s is not None else "n/a"
avg_capitals = f"{df_f6['unique_capitals'].mean():.1f}"
avg_pct_cap_cities = f"{df_f6['pct_capital_cities'].mean():.1f}"

st.markdown(f"""
| Metric | Value |
|--------|-------|
| Artists analysed | {len(df_f6)} |
| Global capital share (events) | {glob_pct:.1f}% |
| Avg. pct_capital per artist | {mean_pct:.1f}% |
| Median pct_capital | {med_pct:.1f}% |
| Ratio capital / non-capital | {glob_ratio:.3f} |
| Avg. capitals visited per artist | {avg_capitals} |
| Avg. pct_capital_cities | {avg_pct_cap_cities}% |
| Pearson r (log listeners to pct_capital) | {r6_str} |
| p-value | {p6_str} |
""")

if r6_s is not None:
    strength6 = "strong" if abs(r6_s) >= 0.7 else "moderate" if abs(r6_s) >= 0.4 else "weak"

    if r6_s > 0.2 and p6_s < 0.05:
        popularity_conclusion = "More popular artists tend to concentrate their shows in capital cities."
    elif r6_s < -0.2 and p6_s < 0.05:
        popularity_conclusion = "More popular artists tour more broadly — their capital share is actually lower."
    else:
        popularity_conclusion = "Streaming popularity is not a meaningful driver of capital-city share — touring decisions appear to be shaped by other factors such as region, genre, or booking strategy."

    sig_text = "statistically significant" if p6_s < 0.05 else "not statistically significant"

    st.markdown(f"""
    <div class="insight-card">
        <h4>Answer to Research Question 2</h4>
        <p>
        On average, <strong style="color:#1DB954">{mean_pct:.1f}%</strong> of all concerts
        take place in capital cities, and each artist visits an average of
        <strong style="color:#1DB954">{avg_capitals}</strong> different capitals.
        However, this share is heavily driven by a small number of dominant hubs —
        particularly London, Berlin, and Dublin — rather than a general preference for capitals across all countries.
        <br><br>
        The relationship between streaming popularity (Last.fm listeners) and capital-city share
        is <strong>{strength6}</strong> (r = {r6_str}, {sig_text}).
        {popularity_conclusion}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="methodology-note">
    <p>
    <strong>Methodological note:</strong>
    Capital cities classified via the RestCountries API (<code>get_capitals.py</code>) —
    245 capitals worldwide. Matching is performed by city name (case-insensitive).
    Cities that serve as both a capital and a major economic centre (e.g. London, Paris)
    may inflate the capital share. Events without a city name are excluded.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()
st.markdown('<div id="geo-frage-3"></div>', unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════
# RESEARCH QUESTION 3
# ══════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown("""
<div class="rq-box">
    <h3>🗺️ Research Question 3</h3>
    <p>How well do the countries where an artist has the highest <strong>listener reach</strong>
    on Last.fm align with the countries where they perform on their Ticketmaster tour?
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Hypothesis:** Artists tend to perform in countries where they have the highest listener counts on Last.fm.

**3 Metrics measure the agreement:**
""")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="insight-card">
        <h4>📐 Jaccard-Similarity</h4>
        <p>Overlap of the Top 10 streaming countries (by listeners) with the tour countries.
        <p>U0 = no Match · 1 = perfect match.</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="insight-card accent">
        <h4>🗺️ Weighted Coverage</h4>
        <p><strong>Listener-weighted:</strong> What share of the listener reach is covered by the tour?
         This is the main metric of this analysis.</p>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="insight-card">
        <h4>📡 Streaming Reach</h4>
        <p>What percentage of streaming countries are also included in the tour?
        This measures whether there are untapped markets.</p>
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
mean_jac = ga["jaccard"].mean()
mean_tc = ga["tour_coverage"].mean()
mean_sr = ga["streaming_reach"].mean()
n_aligned_m = ga["n_aligned"].median()

st.divider()
mean_wc = ga["weighted_coverage"].mean() if "weighted_coverage" in ga.columns else mean_tc
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Artists analysiert", n_artists)
k2.metric("Ø Weighted Coverage", f"{mean_wc:.1%}", help="Listener-gewichteter Anteil")
k3.metric("Ø Jaccard", f"{mean_jac:.3f}")
k4.metric("Ø Streaming Reach", f"{mean_sr:.1%}")
k5.metric("Median aligned Länder", f"{int(n_aligned_m)}")
st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GA2 — GRAPH 1: Scatterplot Listeners vs Jaccard
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 1 — Streaming Popularity vs. Geographic Alignment</div>',
            unsafe_allow_html=True)

st.markdown("""
This scatterplot investigates whether more popular artists tour more closely in line with where their digital fanbase is located. 
The x-axis shows each artist's total Last.fm listener count on a log scale, and the y-axis shows their geo-alignment score — 
by default the listener-weighted coverage, which measures what proportion of an artist's global listener reach is covered by their tour countries.
A score of 1.0 means the artist performs in every country where they have significant listeners; a score of 0.0 means they tour in none of those countries.
The OLS regression line captures the overall trend across all artists.

The colour of each dot can be changed using the selector on the left:
- **Tour Countries** — colours each artist by how many countries they toured in total
- **Tour Coverage** — colours by what share of the artist's tour countries are also among their top streaming countries
- **Streaming Reach** — colours by what share of the artist's streaming countries are actually toured
""")

g1a, g1b = st.columns([1, 3])
with g1a:
    color_by = st.selectbox("Color by",
                            ["n_tour_countries", "tour_coverage", "streaming_reach"],
                            format_func=lambda x: {
                                "n_tour_countries": "Tour Countries",
                                "tour_coverage": "Tour Coverage",
                                "streaming_reach": "Streaming Reach",
                            }[x], key="ga2_color")
    show_labels_g1 = st.checkbox("Show Names", value=False, key="ga2_lbl")

GA2_Y = "weighted_coverage" if "weighted_coverage" in ga.columns else "jaccard"
GA2_Y_LABEL = "Weighted Coverage (Listener-weighted)" if GA2_Y == "weighted_coverage" else "Jaccard-Similarity"
df_g1 = ga.dropna(subset=["listeners", GA2_Y]).copy()
df_g1["log_listeners"] = np.log10(df_g1["listeners"] + 1)

r_g1, p_g1 = stats.pearsonr(df_g1["log_listeners"], df_g1[GA2_Y])
coef_g1 = np.polyfit(df_g1["log_listeners"], df_g1[GA2_Y], 1)
x_line_g1 = np.linspace(df_g1["log_listeners"].min(), df_g1["log_listeners"].max(), 200)
y_line_g1 = np.polyval(coef_g1, x_line_g1)

m1g1, m2g1, m3g1 = st.columns(3)
m1g1.metric("n Artists", len(df_g1))
m2g1.metric("Pearson r", f"{r_g1:.3f}")
m3g1.metric("p-Value", f"{p_g1:.4f}",
            delta="significant " if p_g1 < 0.05 else "not significant ⚠️",
            delta_color="normal" if p_g1 < 0.05 else "inverse")

fig_g1 = px.scatter(
    df_g1, x="log_listeners", y=GA2_Y,
    color=color_by,
    color_continuous_scale="Viridis",
    hover_name="artist_name",
    hover_data={
        "log_listeners": False,
        "jaccard": ":.3f",
        "tour_coverage": ":.1%",
        "streaming_reach": ":.1%",
        "n_aligned": True,
        "n_tour_countries": True,
        "n_streaming": True,
    },
    text="artist_name" if show_labels_g1 else None,
    labels={
        "log_listeners": "log10(Last.fm Listeners)",
        GA2_Y: GA2_Y_LABEL,
        "n_tour_countries": "Tour Countries",
    },
    title=f"Listeners vs. {GA2_Y_LABEL}  |  r = {r_g1:.3f}  |  n = {len(df_g1)}",
    template="plotly_dark",
)
fig_g1.add_trace(go.Scatter(
    x=x_line_g1, y=y_line_g1, mode="lines", name="OLS",
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

# Prepare interpretation
sig_label = "significant " if p_g1 < 0.05 else "not significant ⚠️"
sig_sentence = (
    "This result is statistically significant — the relationship is unlikely to have occurred by chance."
    if p_g1 < 0.05 else
    "This result is not statistically significant — the observed pattern could easily be due to chance in a sample of this size."
)
direction_sentence = (
    "A positive r indicates that more popular artists tend to have a higher geo-alignment score — meaning they tour more closely in line with where their listeners are."
    if r_g1 > 0 else
    "A negative r indicates that more popular artists tend to have a lower geo-alignment score — meaning that despite having more listeners, they cover a smaller share of their streaming markets through touring."
)
if r_g1 > 0.1 and p_g1 < 0.05:
    interpretation_g1 = (
        "More popular artists cover a greater share of their streaming markets through touring — "
        "suggesting that as artists grow in popularity, their touring routes increasingly follow "
        "where their listener demand is strongest."
    )
elif r_g1 < -0.1 and p_g1 < 0.05:
    interpretation_g1 = (
        "Despite having larger and more widespread streaming audiences, more popular artists "
        "actually cover a smaller share of their streaming markets through touring. "
        "This suggests that as artists grow in popularity, their fanbase expands into more countries "
        "than their tours can realistically reach — leaving a growing gap between digital reach and live presence."
    )
else:
    interpretation_g1 = (
        "There is no meaningful relationship between how popular an artist is and how well "
        "their tour geography matches their streaming footprint. "
        "Some highly popular artists cover their streaming markets very well through touring, "
        "while others do not — and the same variation exists among smaller artists. "
        "How well an artist reaches their streaming audience through live shows appears to be "
        "an individual decision rather than something driven by overall popularity."
    )

st.markdown(f"""
<div style="background:#080b14;border:1px solid #232840;border-left:3px solid #6366f1;border-radius:10px;padding:18px 22px;margin-bottom:12px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#818cf8;margin-bottom:10px;">📊 Statistical Analysis</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;">
Pearson r = <strong>{r_g1:.3f}</strong>, p = <strong>{p_g1:.4f}</strong> — <strong>{sig_label}</strong>.
Pearson r measures how strongly streaming popularity and geo-alignment are linearly related — a value close to 0 indicates almost no relationship, while values closer to 1 or -1 indicate a stronger one.
{direction_sentence} {sig_sentence}
</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="background:#080b14;border:1px solid #232840;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;">
{interpretation_g1}
</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# GA2 — GRAPH 2: Top & Bottom Artists — Heatmap Streaming vs. Tour Countries
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 2 — Best and Worst Aligned Artists: Streaming vs. Tour Countries</div>',
            unsafe_allow_html=True)

st.markdown("""
This chart displays the best or worst aligned artists in the dataset, showing three bars side by side for each artist:
- **Streaming Countries (purple)** — the number of countries where the artist appears in Last.fm's top artists list, meaning they have a significant listener presence there
- **Tour Countries (amber)** — the number of countries where the artist has at least one Ticketmaster event
- **Overlap (green)** — the number of countries that appear in both: countries where the artist both has listeners and actually performed

The more the green bar dominates relative to the purple and amber bars, the better aligned the artist is.
Use the selector on the left to switch between the best-aligned artists (those who tour closely where their fans are) and the worst-aligned artists (those with the largest gap between streaming presence and live touring).
You can also change the sorting metric to rank artists by Weighted Coverage, Jaccard Similarity, Tour Coverage, or Streaming Reach.
""")

g3a, g3b = st.columns([1, 3])
with g3a:
    n_show = st.slider("Number of Artists", 5, 20, 10, key="ga2_n")
    show_type = st.radio("Show", ["Best Aligned", "Worst Aligned"], key="ga2_type")
    sort_col = st.selectbox("Sort by",
                            [c for c in ["weighted_coverage", "jaccard", "tour_coverage", "streaming_reach"] if c in ga.columns],
                            format_func=lambda x: metric_labels.get(x, x), key="ga2_sort")

top_df = (ga.dropna(subset=["jaccard", "n_tour_countries", "n_streaming"])
          .nlargest(n_show, sort_col) if show_type == "Best Aligned"
          else ga.dropna(subset=["jaccard", "n_tour_countries", "n_streaming"])
          .nsmallest(n_show, sort_col))

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
    marker_color="#10b981",  # type: ignore
    hovertemplate="%{y}<br>Aligned: %{x} countries  Jaccard=%{customdata:.3f}<extra></extra>",
    customdata=top_df["jaccard"],
))

legend_y = -0.35 + min(n_show * 0.01, 0.15)

fig_g3.update_layout(
    title=show_type + " — Streaming vs. Tour Countries",
    barmode="group",
    xaxis_title="Number of Countries",
    template="plotly_dark",
    paper_bgcolor="#080b14",
    plot_bgcolor="#161c2d",
    font=dict(color="white"),
    height=max(420, n_show * 42),
    xaxis=dict(
        gridcolor="#232840",
        title_standoff=6
    ),
    yaxis=dict(gridcolor="#232840"),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=legend_y,
        xanchor="center",
        x=0.5
    ),
    margin=dict(b=170)
)
with g3b:
    st.plotly_chart(fig_g3, use_container_width=True)

st.markdown("""
<div style="background:#080b14;border:1px solid #232840;border-left:3px solid #10b981;border-radius:10px;padding:18px 22px;margin-bottom:16px;">
<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#10b981;margin-bottom:10px;">🔍 Interpretation</div>
<div style="color:#C8D6E8;font-size:.9rem;line-height:1.65;">
The best-aligned artists show a large green overlap bar relative to their purple and amber bars — meaning they actively perform in the countries where their streaming audience is strongest.
For the worst-aligned artists, two distinct patterns emerge: if the purple bar (streaming) is much larger than the amber bar (tour), the artist has a globally spread fanbase but only tours regionally, leaving many listener markets completely unreached. If the amber bar dominates instead, the artist tours extensively into countries where they have little existing streaming presence, suggesting a deliberate strategy of building new audiences through live performance rather than serving existing ones.
This graph gives a concrete, artist-level answer to Research Question 3 by making the gap — or alignment — between digital reach and live presence visible and comparable across artists.
</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# Summary
st.markdown('<div class="section-title">Summary — Question 3: Geo-Alignment</div>',
            unsafe_allow_html=True)

if mean_jac > 0.4:
    jac_label = "Strong"
    jac_text = "strong"
elif mean_jac > 0.2:
    jac_label = "Moderate"
    jac_text = "moderate"
else:
    jac_label = "Weak"
    jac_text = "weak"

if r_g1 > 0:
    pearson_direction = "positive relationship"
else:
    pearson_direction = "negative relationship"


st.markdown(f"""
| Metric | Average | Note |
|--------|---------|------|
| **Weighted Coverage** | {mean_wc:.1%} | Share of listener reach covered by tour countries |
| **Jaccard Similarity** | {mean_jac:.3f} | {jac_label} overlap between streaming and tour countries |
| **Tour Coverage** | {mean_tc:.1%} | Share of tour countries that are also top streaming countries |
| **Streaming Reach** | {mean_sr:.1%} | Share of streaming countries that are actually toured |
| **Pearson r (Listeners vs. Weighted Coverage)** | {r_g1:.3f} | {pearson_direction} |
""")

if r_g1 > 0.1 and p_g1 < 0.05:
    pearson_conclusion = (
        "The significant positive correlation (r = " + f"{r_g1:.3f}" + ") suggests that more popular artists "
        "are better at aligning their tours with where their listeners are — possibly because they have "
        "more resources and data to plan tours around actual demand."
    )
elif r_g1 < -0.1 and p_g1 < 0.05:
    pearson_conclusion = (
        "The significant negative correlation (r = " + f"{r_g1:.3f}" + ") shows that more popular artists "
        "actually cover a smaller share of their streaming markets through touring. "
        "As artists grow in popularity, their fanbase spreads into more countries than their tours can realistically reach, "
        "creating a widening gap between digital reach and live presence."
    )
else:
    pearson_conclusion = (
        "With r = " + f"{r_g1:.3f}" + " and p = " + f"{p_g1:.4f}" + ", there is no significant relationship "
        "between an artist's popularity and how well their tour geography matches their streaming footprint. "
        "Geo-alignment appears to be an individual characteristic rather than something driven by overall popularity."
    )

if mean_jac > 0.4:
    jac_conclusion = "The average Jaccard similarity of " + f"{mean_jac:.3f}" + " indicates that, on average, artists tour in a strong share of the countries where they have significant listener presence."
elif mean_jac > 0.2:
    jac_conclusion = "The average Jaccard similarity of " + f"{mean_jac:.3f}" + " indicates a moderate overlap — artists do tour in many of their key streaming markets, but a notable share of those markets remains unreached by live performances."
else:
    jac_conclusion = "The average Jaccard similarity of " + f"{mean_jac:.3f}" + " reveals a weak overlap between streaming presence and touring geography — many countries where artists have significant listeners are never visited on tour."

st.markdown(f"""
<div class="insight-card">
    <h4>Answer to Research Question 3</h4>
    <p>
    {jac_conclusion}
    <br><br>
    On average, <strong style="color:#f59e0b">{mean_tc:.1%}</strong> of an artist's tour countries
    are also among their top streaming countries — meaning that the large majority of touring
    does happen in markets where at least some listener base already exists.
    However, only <strong style="color:#10b981">{mean_sr:.1%}</strong> of streaming countries
    are actually visited on tour, which means that a significant share of listener markets
    remain unreached by live performances.
    <br><br>
    {pearson_conclusion}
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="methodology-note">
    <p>
    <strong>Methodological note:</strong>
    Streaming countries are defined as countries where the artist appears in Last.fm's
    geo.getTopArtists list (Top 50 per country).
    Tour countries are defined as countries with at least one Ticketmaster event.
    Jaccard Similarity is calculated as |Streaming ∩ Tour| / |Streaming ∪ Tour|,
    making it robust to differences in dataset size across artists.
    Only artists with data available in both sources are included in this analysis.
    </p>
</div>
""", unsafe_allow_html=True)
