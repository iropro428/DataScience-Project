import streamlit as st
from components.styles import apply_styles
from components.navbar import render_navbar
from components.glossary import apply_glossary_styles

st.set_page_config(
    page_title="Data — From Streams to Stages",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_styles()
render_navbar()
apply_glossary_styles()

st.markdown("""
<div class="page-header">
    <div class="page-header-title-row">
        <span class="page-header-icon">🗄️</span>
        <span class="page-header-title">Data</span>
    </div>
    <p>An overview of all data sources used in this project</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# Overview
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="
    background: #161c2d;
    border: 1px solid #232840;
    border-radius: 14px;
    padding: 32px 36px;
    margin-bottom: 32px;
    max-width: 900px;
">
    <p style="color:#cbd5e1 !important; font-size:1rem; line-height:1.8; margin:0;">
        This project combines data from four sources to analyse the relationship between
        digital streaming popularity and live concert touring.
        Each source contributes a different dimension — listener behaviour, live events,
        geographic context, and chart performance.
    </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# Data Sources 
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📡 Data Sources</div>', unsafe_allow_html=True)

# Metadata for each data source: displayed as styled cards in the section below.
sources = [
    {
        "icon": "🎧",
        "name": "Last.fm API",
        "color": "#818cf8",
        "fields": ["Listener counts per artist", "Play counts", "Top tracks", "Geographic popularity per country"],
        "desc": "Last.fm is a music tracking platform that records what users listen to across devices and services. "
                "For each artist in our dataset, we collected total listener counts, play counts, top tracks, "
                "and a breakdown of listener popularity by country. "
                "These metrics serve as the primary measure of streaming popularity throughout the analysis.",
        "period": "Collected: March 2026",
        "n": "499 artists"
    },
    {
        "icon": "🎟️",
        "name": "Ticketmaster API",
        "color": "#fbbf24",
        "fields": ["Concert dates", "Venue cities and countries", "Capital city classification", "Number of events per artist"],
        "desc": "Ticketmaster is one of the largest concert ticketing platforms worldwide. "
                "We retrieved all available concert events for each artist in our dataset, "
                "including the date, city, and country of each event. "
                "This data forms the basis for all touring analysis — tour scale, geographic reach, and scheduling patterns.",
        "period": "Events from: 2023–2026",
        "n": "All available events per artist"
    },
    {
        "icon": "🌍",
        "name": "RestCountries",
        "color": "#10b981",
        "fields": ["Capital city per country", "Country names and codes", "245 countries covered"],
        "desc": "RestCountries is a publicly available country information dataset. "
                "We used it to classify whether a concert city is a capital city, "
                "which is central to Research Question 2. "
                "The dataset covers 245 countries and territories worldwide.",
        "period": "Static dataset",
        "n": "245 countries"
    },
    {
        "icon": "🗺️",
        "name": "Spotify Chart Data",
        "color": "#f472b6",
        "fields": ["Weekly chart positions", "Chart presence per artist", "Feb 2023 – Feb 2026"],
        "desc": "Weekly Spotify chart data was used to classify artists as chart artists or non-chart artists. "
                "An artist is considered a chart artist if they appeared in the Spotify charts "
                "at least once during the analysis period. "
                "This classification is used in Research Question 3 of the Streaming & Ticket Power analysis.",
        "period": "Feb 2023 – Feb 2026",
        "n": "Weekly snapshots"
    },
]

# Render one styled card per data source.
for src in sources:
    st.markdown(f"""
    <div style="
        background: #161c2d;
        border: 1px solid #232840;
        border-left: 4px solid {src['color']};
        border-radius: 14px;
        padding: 28px 32px;
        margin-bottom: 20px;
    ">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:14px;">
            <span style="font-size:1.8rem;">{src['icon']}</span>
            <h3 style="color:{src['color']} !important; font-size:1.2rem; margin:0;">{src['name']}</h3>
            <span style="color:#475569; font-size:0.8rem; margin-left:auto;">{src['period']} &nbsp;·&nbsp; {src['n']}</span>
        </div>
        <p style="color:#cbd5e1 !important; font-size:0.95rem; line-height:1.75; margin:0 0 16px 0;">
            {src['desc']}
        </p>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">
            {''.join(f'<span style="background:{src["color"]}22; color:{src["color"]}; border-radius:6px; padding:4px 10px; font-size:0.78rem; font-weight:500;">{f}</span>' for f in src['fields'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# Note
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="methodology-note">
    <p>
    <strong>Note on data collection:</strong>
    The original project plan included the use of the Spotify Web API (followers, popularity score).
    However, due to API access restrictions introduced in February 2026 that removed these fields
    in Development Mode, <strong>Last.fm listener counts and play counts</strong> were used
    as alternative popularity proxies. Last.fm metrics are widely used in academic music research
    and have been shown to correlate strongly with cross-platform popularity indicators.
    </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# Visualisation Methods
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Visualisation Methods</div>', unsafe_allow_html=True)

st.markdown("""
<p style="font-size:1rem; color:#cbd5e1;">
All charts in this project are built with <strong>Plotly</strong> and embedded in Streamlit.
Every chart is interactive — you can hover over data points, zoom in, and filter by group.
Here is an overview of the chart types we used and where you can find them.
</p>
""", unsafe_allow_html=True)

# Metadata for each chart type: displayed as a three-column card grid below.
charts = [
    {
        "icon": "🔵",
        "name": "Scatterplot",
        "color": "#818cf8",
        "desc": "Shows the relationship between two variables — each dot represents one artist. Used with a trend line to summarize the overall direction.",
        "used": "Streaming & Ticket Power · Geographic Analysis · Market Time & Scheduling"
    },
    {
        "icon": "📊",
        "name": "Bar Chart",
        "color": "#fbbf24",
        "desc": "Ranks categories by a numeric value. Used both horizontally (cities, capitals) and vertically (listener groups, popularity tiers).",
        "used": "Geographic Analysis · Streaming & Ticket Power"
    },
    {
        "icon": "📊",
        "name": "Grouped Bar Chart",
        "color": "#f59e0b",
        "desc": "Shows multiple bars side by side for each category, allowing direct comparison of several values at once.",
        "used": "Geographic Analysis — Streaming vs. Tour Countries per Artist"
    },
    {
        "icon": "📊",
        "name": "Stacked Bar Chart",
        "color": "#a78bfa",
        "desc": "Stacks multiple values on top of each other within a single bar. Used to show how an artist's total playcount is distributed across their top tracks.",
        "used": "Streaming & Ticket Power — Artist Streaming Profiles"
    },
    {
        "icon": "📦",
        "name": "Box Plot",
        "color": "#10b981",
        "desc": "Shows the distribution of values within a group — median, middle 50%, typical range, and outliers. Used to compare groups side by side.",
        "used": "Streaming & Ticket Power · Geographic Analysis · Market Time & Scheduling"
    },
    {
        "icon": "📉",
        "name": "Histogram",
        "color": "#22d3ee",
        "desc": "Shows how many artists fall into each value range. Used to visualize the distribution of listener counts and weekend share across the dataset.",
        "used": "Streaming & Ticket Power — Listener Distribution · Market Time & Scheduling — Weekend Share"
    },
]

# Render one card per chart type, distributed across three columns.
v_cols = st.columns(3)
for i, chart in enumerate(charts):
    with v_cols[i % 3]:
        st.markdown(f"""
        <div style="
            background:#161c2d;
            border:1px solid #232840;
            border-left:4px solid {chart['color']};
            border-radius:12px;
            padding:20px 22px;
            margin-bottom:16px;
            height:280px;
        ">
            <div style="font-size:1.4rem;margin-bottom:8px;">{chart['icon']}</div>
            <div style="color:{chart['color']} !important;font-weight:700;font-size:1rem;margin-bottom:10px;">
                {chart['name']}
            </div>
            <p style="color:#cbd5e1 !important;font-size:0.9rem;line-height:1.6;margin:0 0 12px 0;">
                {chart['desc']}
            </p>
            <div style="font-size:0.78rem;color:#475569 !important;border-top:1px solid #232840;padding-top:10px;">
                📍 {chart['used']}
            </div>
        </div>
        """, unsafe_allow_html=True)
