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

# ── Load Data ──────────────────────────────────────────────────────────────
data_path = "data/processed/final_dataset.csv"
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    n_artists = len(df)
    n_events = int(df["total_events"].sum()) if "total_events" in df.columns else "—"
    avg_listen = f"{int(df['listeners'].mean()):,}" if "listeners" in df.columns else "—"
    if "tour_countries" in df.columns:
        n_countries = df["tour_countries"].dropna().str.split(",").explode().str.strip().nunique()
    elif "n_tour_countries" in df.columns:
        n_countries = int(df["n_tour_countries"].max())
    else:
        n_countries = "—"
else:
    n_artists = n_events = n_countries = avg_listen = "—"

# ══════════════════════════════════════════════════════════════════════════
# WHAT WE INVESTIGATE
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔭 What We Investigate</div>', unsafe_allow_html=True)
st.markdown("""<div style="
    background:#161c2d; border:1px solid #232840; border-radius:14px;
    padding:32px 36px; margin-bottom:32px; max-width:900px;
">
    <p style="color:#cbd5e1 !important;font-size:1rem;line-height:1.8;margin:0 0 16px 0;">
        Streaming platforms such as Last.fm and Spotify generate millions of data points every day —
        listener counts, play counts, chart positions. But how well do these digital signals
        reflect what artists actually do on stage?
    </p>
    <p style="color:#cbd5e1 !important;font-size:1rem;line-height:1.8;margin:0 0 16px 0;">
        We combine <strong style="color:#818cf8 !important;">Last.fm data</strong> from 499 international
        artists with their <strong style="color:#fbbf24 !important;">Ticketmaster concert data</strong>
        from 2023–2026 and analyse three core areas:
        the relationship between streaming popularity and tour scale,
        geographic patterns in touring, and the temporal structure of concert scheduling.
    </p>
    <p style="color:#94a3b8 !important;font-size:0.9rem;line-height:1.6;margin:0;font-style:italic;">
        Data collected: March 2026 · Analysis period: Jan 2023 – Feb 2026 · 499 Artists · 9 Research Questions
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# THREE ANALYSIS AREAS
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📂 The Three Analysis Areas</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
card_style = """
    border-radius:16px; padding:32px 28px 28px;
    border:1px solid {border}; background:{bg};
    position:relative; overflow:hidden;
    min-height: 610px;
"""
for col, icon, title, color, border, bg, desc, qs, page in [
    (
        c1, "🎟️",
        "Streaming & Ticket Power",
        "#818cf8", "#2e3557", "#12153a",
        "Does digital popularity correlate with the scale of an artist's tour? "
        "We examine whether artists with more Last.fm listeners play larger tours, "
        "how concentrated their streaming is on a few hits, and whether Spotify chart "
        "presence is associated with higher listener counts on Last.fm.",
        ["Listeners vs. Tour Scale", "Streaming Concentration vs. Tour Intensity", "Chart Artists vs. Non-Chart"],
        "pages/2_Streaming_Ticket.py"
    ),
    (
        c2, "🗺️",
        "Geographic Analysis",
        "#fbbf24", "#2e3557", "#12153a",
        "Where do artists go on tour — and does this align with their geographic streaming popularity? "
        "We analyse whether artists revisit cities, how many concerts take place in capital cities, "
        "and how well streaming countries and tour countries overlap.",
        ["Revisit vs. New Cities", "Capital vs. Non-Capital Cities", "Streaming Countries vs. Tour Countries"],
        "pages/3_Geographic.py"
    ),
    (
        c3, "📅",
        "Market Time & Scheduling",
        "#10b981", "#2e3557", "#12153a",
        "When and how do artists plan their shows? We examine the number of days between "
        "performances, whether more popular artists play more frequently on weekends, "
        "and how far in advance tickets go on sale relative to artist popularity.",
        ["Days Between Shows", "Weekend Concerts", "Advance Sale Lead Time"],
        "pages/4_Scheduling.py"
    ),
]:
    with col:
        st.markdown(f"""<div style="{card_style.format(border=border, bg=bg)}">
            <div style="font-size:2rem;margin-bottom:14px;">{icon}</div>
            <h3 style="color:{color} !important;font-size:1.2rem;font-weight:700;
                margin:0 0 14px 0;line-height:1.3;">{title}</h3>
            <p style="color:#94a3b8 !important;font-size:1rem;line-height:1.7;
                margin:0 0 20px 0; min-height: 150px;">{desc}</p>
            <div style="border-top:1px solid {border};padding-top:16px;">
                <div style="font-size:0.85rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:.1em;color:#475569 !important;margin-bottom:10px;">
                    Research Questions
                </div>
                {''.join(f"""<div style="display:flex;align-items:center;gap:8px;margin-bottom:7px;">
                    <span style="background:{color}22;color:{color} !important;
                        border-radius:50%;width:22px;height:22px;display:flex;
                        align-items:center;justify-content:center;
                        font-size:0.8rem;font-weight:700;flex-shrink:0;">{i + 1}</span>
                    <span style="color:#cbd5e1 !important;font-size:1rem;">{q}</span>
                </div>""" for i, q in enumerate(qs))}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.page_link(page, label="Go to Analysis →", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔬 Methodology Overview</div>', unsafe_allow_html=True)

me1, me2, me3, me4 = st.columns(4)
for col, icon, title, text in [
    (me1, "📥", "Data Collection", "Last.fm API for popularity metrics, Ticketmaster for concert data, RestCountries for capital city information."),
    (me2, "🔗", "Data Join", "Linked via normalised artist name. 499 artists with complete data available in both sources."),
    (me3, "📊", "Analysis", "Correlation analysis, Mann-Whitney U, Kruskal-Wallis, OLS regression, Jaccard Similarity."),
    (me4, "🖥️", "Visualisation", "Interactive Plotly charts embedded in Streamlit. All charts are filterable and zoomable."),
]:
    with col:
        st.markdown(f"""<div style="background:#161c2d;border:1px solid #232840;border-radius:10px;
            padding:18px;text-align:center;min-height:180px;">
            <div style="font-size:1.6rem;margin-bottom:8px;">{icon}</div>
            <div style="color:#f1f5f9 !important;font-weight:600;font-size:1rem;
                margin-bottom:8px;">{title}</div>
            <div style="color:#475569 !important;font-size:0.9rem;line-height:1.55;">{text}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# KEY FINDINGS
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">💡 Key Findings</div>', unsafe_allow_html=True)
st.markdown("""<div style="
    background:linear-gradient(135deg,#12153a 0%,#0f1a2e 100%);
    border:1px solid #4338ca; border-radius:16px; padding:36px 40px;
">
    <p style="color:#f1f5f9 !important;font-size:1.1rem;font-weight:500;
        line-height:1.8;margin:0 0 18px 0;">
        Our analyses show: <strong style="color:#818cf8 !important;">
        Digital streaming popularity and physical touring activity are related —
        but the relationship is weaker and more nuanced than one might expect.</strong>
    </p>
    <p style="color:#94a3b8 !important;font-size:1rem;line-height:1.8;margin:0 0 18px 0;">
        More popular artists do play larger tours, but the variation within popularity groups is substantial.
        Geographically, artists show a clear preference for capital cities and tend to revisit
        established markets — both consistent with strategic tour planning.
        The overlap between streaming countries and tour countries is moderate:
        artists actively enter new markets beyond their existing digital footprint,
        particularly as their fanbase grows faster than their touring reach can cover.
    </p>
    <p style="color:#94a3b8 !important;font-size:1rem;line-height:1.8;margin:0;">
        Streaming data is a useful but incomplete signal for touring decisions.
        Additional factors such as venue availability, management strategy,
        and regional marketing budgets play an important role alongside digital popularity.
    </p>
</div>
""", unsafe_allow_html=True)
