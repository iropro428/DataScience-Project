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

# ── Daten laden ────────────────────────────────────────────────────────────
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
# DATENSATZ-KENNZAHLEN
# ══════════════════════════════════════════════════════════════════════════
m1, m2, m3, m4 = st.columns(4)
for col, val, label in [
    (m1, n_artists, "Analysierte Artists"),
    (m2, n_events, "Konzert-Events"),
    (m3, n_countries, "Laender abgedeckt"),
    (m4, avg_listen, "Ø Last.fm Listeners"),
]:
    col.metric(label, val)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# WAS WIR UNTERSUCHEN
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔭 Was wir untersuchen</div>', unsafe_allow_html=True)
st.markdown("""<div style="
    background:#161c2d; border:1px solid #232840; border-radius:14px;
    padding:32px 36px; margin-bottom:32px; max-width:900px;
">
    <p style="color:#cbd5e1 !important;font-size:1rem;line-height:1.8;margin:0 0 16px 0;">
        Streaming-Plattformen wie Last.fm und Spotify erzeugen taeglich Millionen von Datenpunkten —
        Listener-Zahlen, Playcounts, Chart-Positionen. Doch wie gut korrelieren diese digitalen Signale
        mit dem, was Kuenstler tatsaechlich auf der Buehne tun?
    </p>
    <p style="color:#cbd5e1 !important;font-size:1rem;line-height:1.8;margin:0 0 16px 0;">
        Wir verbinden <strong style="color:#818cf8 !important;">Last.fm-Daten</strong> von 499 internationalen
        Kuenstlern mit deren <strong style="color:#fbbf24 !important;">Ticketmaster-Konzertdaten</strong>
        aus dem Zeitraum 2022–2026 und analysieren drei Kernbereiche:
        die Verbindung zwischen Streaming-Popularitaet und Tourumfang,
        geografische Muster von Tourneen, sowie zeitliche Strukturen der Konzertplanung.
    </p>
    <p style="color:#94a3b8 !important;font-size:.9rem;line-height:1.6;margin:0;font-style:italic;">
        Datenerhebung: Maerz 2026 · Analysezeitraum: Jan 2022 – Feb 2026 · 499 Artists · 9 Forschungsfragen
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# DIE DREI UNTERTHEMEN — CARDS
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📂 Die drei Analysebereiche</div>', unsafe_allow_html=True)

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
            "Korreliert digitale Beliebtheit mit dem Umfang einer Tournee? "
            "Wir untersuchen ob Artists mit mehr Last.fm-Listeners groessere Touren spielen, "
            "wie konzentriert ihr Streaming auf wenige Hits ist — und ob Spotify-Chart-Praesenz "
            "mit mehr Last.fm-Listeners einhergeht.",
            ["Listeners vs. Tour-Umfang", "Streaming-Konzentration vs. Tour-Intensitaet",
             "Chart-Artists vs. Non-Chart"],
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
                    Forschungsfragen
                </div>
                {''.join(f"""<div style="display:flex;align-items:center;gap:8px;margin-bottom:7px;">
                    <span style="background:{color}22;color:{color} !important;
                        border-radius:50%;width:20px;height:20px;display:flex;
                        align-items:center;justify-content:center;
                        font-size:.7rem;font-weight:700;flex-shrink:0;">{i + 1}</span>
                    <span style="color:#cbd5e1 !important;font-size:.82rem;">{q}</span>
                </div>""" for i, q in enumerate(qs))}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.page_link(page, label=f"Zur Analyse →", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# METHODIK (kompakt)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔬 Methodik im Ueberblick</div>', unsafe_allow_html=True)

me1, me2, me3, me4 = st.columns(4)
for col, icon, title, text in [
    (me1, "📥", "Datenerhebung",
     "Last.fm API fuer Popularity-Metriken, Ticketmaster fuer Konzertdaten, RestCountries fuer Hauptstaedte."),
    (me2, "🔗", "Datenjoin",
     "Verknuepfung ueber normalisierten Kuenstlernamen. 499 Artists mit vollstaendigen Daten in beiden Quellen."),
    (me3, "📊", "Analysen", "Korrelationsanalysen, Mann-Whitney U, Kruskal-Wallis, OLS-Regression, Jaccard-Similarity."),
    (me4, "🖥️", "Visualisierung", "Interaktive Plotly-Charts in Streamlit. Alle Grafiken filterbar und zoombar."),
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

# ══════════════════════════════════════════════════════════════════════════
# FAZIT / PROJEKTANTWORT
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">💡 Was wir aus dem Projekt mitnehmen</div>', unsafe_allow_html=True)
st.markdown("""<div style="
    background:linear-gradient(135deg,#12153a 0%,#0f1a2e 100%);
    border:1px solid #4338ca; border-radius:16px; padding:36px 40px;
">
    <p style="color:#f1f5f9 !important;font-size:1.05rem;font-weight:500;
        line-height:1.8;margin:0 0 18px 0;">
        Unsere Analysen zeigen: <strong style="color:#818cf8 !important;">
        Digitale Streaming-Popularitaet und physische Tourneerealitaet
        haengen zusammen — aber nicht so direkt wie man erwarten wuerde.</strong>
    </p>
    <p style="color:#94a3b8 !important;font-size:.95rem;line-height:1.8;margin:0 0 18px 0;">
        Populaere Artists spielen zwar groessere Touren, aber die Streuung ist erheblich.
        Geografisch bevorzugen Artists Hauptstaedte und kehren regelmaessig in
        bewaehlte Staedte zurueck — was auf strategische Tourplanung hindeutet.
        Die Uebereinstimmung zwischen Streaming-Laendern und Tour-Laendern
        ist moderat: Kuenstler erschliessen aktiv neue Maerkte jenseits ihres
        digitalen Footprints.
    </p>
    <p style="color:#94a3b8 !important;font-size:.95rem;line-height:1.8;margin:0;">
        Streaming-Daten sind ein nuetzliches, aber unvollstaendiges Signal fuer
        Tourneeentscheidungen. Weitere Faktoren wie Venue-Verfuegbarkeit,
        Management-Strategie und regionale Marketingbudgets spielen ebenfalls
        eine wesentliche Rolle.
    </p>
</div>
""", unsafe_allow_html=True)
