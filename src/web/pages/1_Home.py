import streamlit as st
import pandas as pd
import os

from components.styles import apply_styles
from components.navbar import render_navbar
from components.glossary import apply_glossary_styles, tt

st.set_page_config(
    page_title="From Streams to Stages",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_styles()
render_navbar()
apply_glossary_styles()

# load data
data_path = "data/processed/final_dataset.csv"
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    n_artists = len(df)
    n_events = int(df["total_events"].sum()) if "total_events" in df.columns else "—"
    n_countries = int(df["countries"].max()) if "countries" in df.columns else "—"
    avg_listen = f"{int(df['listeners'].mean()):,}" if "listeners" in df.columns else "—"
else:
    n_artists = n_events = n_countries = avg_listen = "—"

# ══════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""

""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# DATASET METRICS
# ══════════════════════════════════════════════════════════════════════════
m1, m2, m3, m4 = st.columns(4)
for col, val, label in [
    (m1, n_artists, "Artists analyzed"),
    (m2, n_events, "Concert events"),
    (m3, n_countries, "Countries covered"),
    (m4, avg_listen, "Ø Last.fm listeners"),
]:
    col.metric(label, val)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# WHAT WE ANALYZE
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔭 What we analyze</div>', unsafe_allow_html=True)
st.markdown("""<div style="
    background:#161c2d; border:1px solid #232840; border-radius:14px;
    padding:32px 36px; margin-bottom:32px; max-width:900px;
">
    <p style="color:#cbd5e1 !important;font-size:1rem;line-height:1.8;margin:0 0 16px 0;">
        Streaming platforms such as Last.fm and Spotify generate millions of data points every day —
        listener counts, play counts, and chart rankings. But how strongly do these digital signals
        relate to what artists actually do on stage?
    </p>
    <p style="color:#cbd5e1 !important;font-size:1rem;line-height:1.8;margin:0 0 16px 0;">
        We combine <strong style="color:#818cf8 !important;">Last.fm data</strong> from 499 international
        artists with their <strong style="color:#fbbf24 !important;">Ticketmaster concert data</strong>
        from 2022–2026 and analyze three core dimensions:
        the relationship between streaming popularity and tour scale,
        geographic patterns of touring activity, and temporal structures
        of concert planning.
    </p>
    <p style="color:#94a3b8 !important;font-size:.9rem;line-height:1.6;margin:0;font-style:italic;">
        Data collection: March 2026 · Analysis period: Jan 2022 – Feb 2026 · 499 artists · 9 research questions
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# THE THREE SUBTOPICS — CARDS
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📂 The three analysis areas</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

card_style = """
    border-radius:16px; padding:32px 28px 28px;
    border:1px solid {border}; background:{bg};
    position:relative; overflow:hidden; height:100%;
"""

for col, icon, title, color, border, bg, desc, qs, page in [
    (
            c1, "🎟️",
            "Streaming & Ticket Power",
            "#818cf8", "#2e3557", "#12153a",
            "Does digital popularity correlate with the scale of an artist's tour? "
            "We analyze whether artists with more Last.fm listeners perform larger tours, "
            "how concentrated their streaming activity is around a few hit songs — "
            "and whether Spotify chart appearances are associated with higher "
            "Last.fm listener counts.",
            ["Listeners vs. tour scale", "Streaming concentration vs. tour intensity",
             "Chart artists vs. non-chart artists"],
            "pages/2_Streaming_Ticket.py"
    )
]:
    with col:
        st.markdown(f"""<div style="{card_style.format(border=border, bg=bg)}">
            <div style="font-size:2rem;margin-bottom:14px;">{icon}</div>
            <h3 style="color:{color} !important;font-size:1.05rem;font-weight:700;
                margin:0 0 14px 0;line-height:1.3;">{title}</h3>
            <p style="color:#94a3b8 !important;font-size:.875rem;line-height:1.7;
                margin:0 0 20px 0;">{desc}</p>
            <div style="border-top:1px solid {border};padding-top:16px;">
                <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:.1em;color:#475569 !important;margin-bottom:10px;">
                    Research questions
                </div>
                {''.join(f"""<div style="display:flex;align-items:center;gap:8px;margin-bottom:7px;">
                    <span style="background:{color}22;color:{color} !important;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:700;flex-shrink:0;">{i + 1}</span>
                    <span style="color:#cbd5e1 !important;font-size:.82rem;">{q}</span>
                </div>""" for i, q in enumerate(qs))}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.page_link(page, label=f"Go to analysis →", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔬 Methodology overview</div>', unsafe_allow_html=True)

me1, me2, me3, me4 = st.columns(4)
for col, icon, title, text in [
    (me1, "📥", "Data collection",
     "Last.fm API for popularity metrics, Ticketmaster for concert data, RestCountries for capital city information, Spotify Charts for weekly chart data."),
    (me2, "🔗", "Data integration",
     "Datasets merged via normalized artist names. 499 artists with complete data across both sources."),
    (me3, "📊", "Analyses", "Correlation analysis, Mann-Whitney U, Kruskal-Wallis, OLS regression, Jaccard similarity."),
    (me4, "🖥️", "Visualization", "Interactive Plotly charts in Streamlit. All graphs are filterable and zoomable."),
]:
    with col:
        st.markdown(f"""<div style="background:#161c2d;border:1px solid #232840;border-radius:10px;
            padding:18px;text-align:center;height:100%;">
            <div style="font-size:1.6rem;margin-bottom:8px;">{icon}</div>
            <div style="color:#f1f5f9 !important;font-weight:600;font-size:.85rem;
                margin-bottom:8px;">{title}</div>
            <div style="color:#475569 !important;font-size:.78rem;line-height:1.55;">{text}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)