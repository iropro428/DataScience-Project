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

# ── CSS ───────────────────────────────────────────────


# ── Header ─────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>🎟️ Streaming &amp; Ticket Power</h1>
    <p>Wie stark haengt digitale Beliebtheit auf Last.fm mit dem Umfang und der Intensitaet von Tourneen zusammen?</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#161c2d;border:1px solid #232840;border-radius:14px;
    padding:24px 28px;margin-bottom:28px;">
    <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;
        letter-spacing:.12em;color:#475569 !important;margin-bottom:14px;">
        Inhaltsübersicht — Forschungsfragen
    </div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <a href="#frage-1" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">1</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                Wie korreliert die Anzahl der Last.fm Listeners mit dem Umfang einer Tournee?
            </span>
        </a>
        <a href="#frage-2" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">2</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                Wie beeinflusst die Konzentration des Streamings auf wenige Top-Tracks die Tour-Intensitaet?
            </span>
        </a>
        <a href="#frage-3" style="display:flex;align-items:center;gap:12px;
            text-decoration:none;padding:10px 14px;border-radius:8px;
            background:#1d2440;border:1px solid #2e3557;transition:all .15s;">
            <span style="background:#4338ca;color:white !important;border-radius:50%;
                width:24px;height:24px;display:flex;align-items:center;justify-content:center;
                font-size:.75rem;font-weight:700;flex-shrink:0;">3</span>
            <span style="color:#cbd5e1 !important;font-size:.9rem;">
                Unterscheiden sich Last.fm Listeners zwischen Chart-Artists und Non-Chart-Artists?
            </span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div id="frage-1"></div>', unsafe_allow_html=True)


# ── Load Data ──────────────────────────────────────────
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
    st.error("⚠️ Dataset nicht gefunden. Bitte zuerst die Collection-Skripte ausführen.")
    st.code("python scripts/collect_artists_lastfm.py\npython scripts/collect_ticketmaster.py\npython scripts/join_data.py")
    st.stop()


# ── Genre Helper ───────────────────────────────────────
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
**Was messen wir?**
Wir untersuchen, ob Künstler mit mehr Last.fm-Listeners auch tendenziell mehr Live-Konzerte
veranstalten. Der Last.fm Listener Count gibt an, wie viele eindeutige Nutzer einen Künstler
gehört haben — ein anerkannter akademischer Proxy für digitale Popularität.
Tour-Skala = Gesamtzahl der Ticketmaster-Events von 2022–2026.

**Warum ist das relevant?**  
Wenn digitale Popularität live-Aktivität vorhersagt, bestätigt das, dass Streaming-Plattformen
als Planungsgrundlage für die Live-Musikbranche dienen können.
""")

st.divider()

# ══════════════════════════════════════════════════════
# GRAPH 1 — Scatterplot
# ══════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 1 — Scatterplot: Last.fm Listeners vs. Anzahl Events</div>',
            unsafe_allow_html=True)

st.markdown("""
Ein **Scatterplot** zeigt die Beziehung zwischen zwei numerischen Variablen direkt.
Jeder Punkt = ein Künstler. Die **Trendlinie (OLS-Regression)** zeigt die Richtung der Korrelation.
Das schraffierte Band = 95%-Konfidenzintervall.
Nutze die Filter, um Teilmengen der Daten zu erkunden und zu sehen wie sich r verändert.
""")

# ── Filter Controls ────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    listener_range = st.slider(
        "🎧 Listener-Bereich (Last.fm)",
        min_value=int(df["listeners"].min()),
        max_value=int(df["listeners"].max()),
        value=(int(df["listeners"].min()), int(df["listeners"].max())),
        key="g1_lr"
    )
with c2:
    event_max = st.slider(
        "🎟️ Max. Events (Ausreißer entfernen)",
        min_value=5,
        max_value=int(df["total_events"].max()),
        value=int(df["total_events"].max()),
        key="g1_em"
    )

c3, c4 = st.columns([3, 1])
with c3:
    selected_genres = st.multiselect(
        "🎵 Genre-Filter (leer = alle)",
        options=top_genres, default=[], key="g1_genres"
    )
with c4:
    show_labels = st.checkbox("Künstlernamen anzeigen", value=False, key="g1_lbl")

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

# ── Stats ──────────────────────────────────────────────
if len(df1) >= 5:
    r, p = stats.pearsonr(df1["listeners"], df1["total_events"])
    r2 = r ** 2
    strength = "stark" if abs(r) >= 0.7 else "moderat" if abs(r) >= 0.4 else "schwach"
    direction = "positiv" if r > 0 else "negativ"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("n Künstler", len(df1))
    m2.metric("Pearson r", f"{r:.3f}")
    m3.metric("R² (Varianz erklärt)", f"{r2:.1%}")
    m4.metric("p-Wert", f"{p:.4f}",
              delta="signifikant ✅" if p < 0.05 else "nicht signifikant ⚠️",
              delta_color="normal" if p < 0.05 else "inverse")

    # ── Plot ───────────────────────────────────────────
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
            "listeners": "Last.fm Listeners",
            "total_events": "Anzahl geplanter Events",
            "tags": "Genre-Tags"
        },
        title=f"Last.fm Listeners vs. Tour-Skala  |  r = {r:.3f}  |  n = {len(df1)} Künstler",
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

    # ── Interpretation ─────────────────────────────────
    st.markdown(f"""
    <div class="insight-card">
        <h4>📊 Statistisches Ergebnis</h4>
        <p>
        Der Pearson-Korrelationskoeffizient beträgt <strong style="color:#1DB954">r = {r:.3f}</strong>
        — das ist eine <strong>{strength}e {direction}e Korrelation</strong> zwischen Last.fm Listeners 
        und Tour-Skala. Der R²-Wert von <strong style="color:#1DB954">{r2:.1%}</strong> bedeutet, 
        dass der Listener-Count {r2:.1%} der Varianz in der Event-Anzahl erklärt.
        Das Ergebnis ist <strong>{"statistisch signifikant ✅" if p < 0.05 else "nicht statistisch signifikant ⚠️"}</strong>
        (p = {p:.4f}, n = {len(df1)}).
        </p>
    </div>
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>
        Künstler mit mehr Last.fm Listeners tendieren dazu, 
        {"mehr" if r > 0 else "weniger"} Konzerte zu veranstalten.
        {"Dies unterstützt die Hypothese, dass digitale Popularität mit Live-Aktivität zusammenhängt."
    if r > 0 and p < 0.05 and abs(r) >= 0.4 else
    "Der Zusammenhang ist jedoch schwach — digitale Popularität allein prognostiziert die Tour-Skala nur bedingt."
    if abs(r) < 0.4 else
    "Der Zusammenhang ist moderat — andere Faktoren wie Genre, Management und Budget spielen ebenfalls eine wichtige Rolle."}
        <br><br>
        <strong>Hinweis:</strong> Korrelation impliziert keine Kausalität. Ein hoher Listener Count 
        könnte auch eine Folge vergangener Touren sein, nicht nur deren Vorhersage.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("Zu wenig Datenpunkte nach Filterung. Filter bitte anpassen.")

st.divider()

# ══════════════════════════════════════════════════════
# GRAPH 2 — Bar Chart (Quartile)
# ══════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 2 — Ø Events pro Listener-Quartil</div>',
            unsafe_allow_html=True)

st.markdown("""
Um das Muster klarer zu zeigen, teilen wir Künstler in gleich große **Gruppen nach Listener-Count** auf.
Das **Balkendiagramm** zeigt die durchschnittliche Event-Anzahl pro Gruppe.
Im Gegensatz zum Scatterplot reduziert diese Ansicht Rauschen und macht strukturelle Trends
sofort ablesbar — perfekt für eine zusammenfassende Aussage.
""")

qa, qb = st.columns([1, 3])
with qa:
    n_groups = st.select_slider(
        "Anzahl Gruppen",
        options=[3, 4, 5, 6, 8, 10],
        value=4, key="g2_ng"
    )
    agg = st.radio("Aggregation", ["Mittelwert", "Median"], index=0, key="g2_agg")

try:
    df2 = df.copy()
    labels = [f"G{i + 1}" for i in range(n_groups)]
    df2["group"] = pd.qcut(df2["listeners"], q=n_groups, labels=labels, duplicates="drop")
    agg_fn = "mean" if agg == "Mittelwert" else "median"

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
            "<b>Gruppe %{x}</b><br>"
            f"{agg} Events: %{{y:.1f}}<br>"
            "Künstler: %{customdata[0]}<br>"
            "Ø Listeners: %{customdata[1]:,.0f}<extra></extra>"
        )
    ))
    fig2.update_layout(
        title=f"{agg} Anzahl Events pro Listener-Gruppe  ({n_groups} Gruppen, G1=wenigste Listeners)",
        xaxis_title="Listener-Gruppe",
        yaxis_title=f"{agg} Events",
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
        <h4>📈 Gruppenvergleich</h4>
        <p>
        Künstler der Gruppe mit den <strong>meisten Listeners</strong> veranstalten im Schnitt
        <strong style="color:#1DB954">{gn_val:.1f} Events</strong>, 
        die Gruppe mit den wenigsten Listeners nur <strong>{g1_val:.1f} Events</strong> — 
        eine Differenz von <strong style="color:#1DB954">{diff:+.1f} Events</strong>.
        {"Das Muster ist über alle Gruppen konsistent und bestätigt den monotonen Zusammenhang." if diff > 2 else
    "Der Unterschied zwischen den Gruppen ist gering — Listener-Count ist kein starker Prädiktor für Tour-Skala."}
        </p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.warning(f"Gruppierung fehlgeschlagen: {e}")

st.divider()

# ══════════════════════════════════════════════════════
# GRAPH 3 — Histogram (Verteilung)
# ══════════════════════════════════════════════════════
st.markdown('<div class="section-title">📉 Graph 3 — Verteilung der Last.fm Listeners</div>',
            unsafe_allow_html=True)

st.markdown("""
Bevor wir Korrelationen interpretieren, müssen wir die **Datenverteilung** verstehen.
Ein **Histogramm** zeigt, wie viele Künstler in welchen Listener-Bereichen liegen.
Eine stark schiefe Verteilung (wenige Superstars, viele Mid-Tier-Künstler) beeinflusst
den Pearson-Koeffizienten und muss bei der Interpretation berücksichtigt werden.
""")

ha, hb = st.columns([1, 3])
with ha:
    n_bins = st.slider("Anzahl Bins", 10, 80, 30, key="g3_bins")
    log_x = st.checkbox("Logarithmische X-Achse", value=False, key="g3_log")
    show_rug = st.checkbox("Einzelpunkte (Rug-Plot)", value=False, key="g3_rug")

with hb:
    x_data = np.log10(df["listeners"] + 1) if log_x else df["listeners"]
    x_lab = "log₁₀(Last.fm Listeners)" if log_x else "Last.fm Listeners"

    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(
        x=x_data, nbinsx=n_bins, name="Künstler",
        marker=dict(color="#1DB954", opacity=0.8,
                    line=dict(width=0.5, color="#0e0e0e")),
        hovertemplate="Listeners: %{x}<br>Anzahl: %{y}<extra></extra>"
    ))
    if show_rug:
        fig3.add_trace(go.Scatter(
            x=x_data, y=[-2] * len(x_data), mode="markers",
            marker=dict(symbol="line-ns", size=8, color="#1DB954", opacity=0.3,
                        line=dict(width=1, color="#1DB954")),
            name="Einzelkünstler", hoverinfo="skip"
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
        title="Verteilung der Last.fm Listeners über alle Künstler",
        xaxis_title=x_lab, yaxis_title="Anzahl Künstler",
        template="plotly_dark",
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"), height=380,
        xaxis=dict(gridcolor="#333", tickformat=","),
        yaxis=dict(gridcolor="#333"), showlegend=False
    )
    st.plotly_chart(fig3, use_container_width=True)

skew = float(pd.Series(df["listeners"]).skew())
st.markdown(f"""<div class="insight-card">
<h4>📐 Verteilungsanalyse</h4>
<p>
Die Verteilung ist <strong>{"stark" if abs(skew) > 1 else "moderat"} 
{"rechtsschief" if skew > 0 else "linksschief"}</strong> (Schiefe = {skew:.2f}).
Das ist typisch für Popularitätsdaten — wenige globale Superstars dominieren,
während die Mehrheit der Künstler weit weniger Listeners hat.
{"Die logarithmische Transformation (Checkbox oben) normalisiert diese Verteilung." if abs(skew) > 1 else ""}
<br/>
<strong>Implikation für die Korrelation:</strong>
Wenige Ausreißer (Superstars) können den Pearson-r stark beeinflussen.
Nutze den Slider in Graph 1, um extreme Ausreißer zu entfernen und zu beobachten,
wie sich r verändert — das zeigt die Robustheit der Korrelation.
</p>
</div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════
# ZUSAMMENFASSUNG F1
# ══════════════════════════════════════════════════════
st.markdown('<div class="section-title">Zusammenfassung — Research Question 1</div>',
            unsafe_allow_html=True)

if len(df) >= 5:
    r_all, p_all = stats.pearsonr(df["listeners"], df["total_events"])
    r2_all = r_all ** 2
    st_all = "stark" if abs(r_all) >= 0.7 else "moderat" if abs(r_all) >= 0.4 else "schwach"

    st.markdown(f"""
    | Metrik | Wert |
    |--------|------|
    | Stichprobengröße (n) | {len(df)} Künstler |
    | Pearson r | {r_all:.3f} |
    | R² | {r2_all:.1%} |
    | p-Wert | {p_all:.4f} |
    | Statistisch signifikant | {'Ja (p < 0,05) ✅' if p_all < 0.05 else 'Nein (p ≥ 0,05) ⚠️'} |
    | Korrelationsstärke | {st_all.capitalize()} |
    """)

    answer = (
            f"Es besteht eine **{st_all}e {"positive" if r_all > 0 else "negative"} Korrelation** "
            f"(r = {r_all:.3f}) zwischen Last.fm Listener Count und Tour-Skala. "
            f"Der Listener Count erklärt ca. **{r2_all:.1%}** der Varianz in der Anzahl geplanter Events. "
            + ("Dies bestätigt, dass digitale Popularität mit realer Tourplanung zusammenhängt."
               if p_all < 0.05 and r_all > 0.3 else
               "Der Zusammenhang ist jedoch statistisch schwach — weitere Faktoren müssen berücksichtigt werden.")
    )
    st.markdown(f"""<div class="insight-card">
        <h4>🎯 Antwort auf Research Question 1</h4>
        <p>{answer}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("""<div class="methodology-note">
    <p>
    <strong>Methodische Anmerkung:</strong> Last.fm Listener Counts wurden als statischer Snapshot (März 2026)
    erhoben, da Spotify im Februar 2026 die follower- und popularity-Felder für Development-Mode-Apps deaktiviert hat.
    Ticketmaster-Eventdaten umfassen Januar 2022–Dezember 2026. Die Analyse beschränkt sich auf Künstler
    mit mindestens einem Event auf Ticketmaster und vorhandenen Last.fm-Daten.
    </p>
</div>""", unsafe_allow_html=True)

st.markdown('<div id="frage-2"></div>', unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════
# RESEARCH QUESTION 2 — Streaming-Konzentration vs. Tour-Intensität
# ══════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown("""<div class="rq-box">
    <h3>🔬 Research Question 2</h3>
    <p>How does the concentration of an artist's streaming activity on a few top tracks
    relate to the intensity of their touring, measured by events per year?</p>
</div>""", unsafe_allow_html=True)

st.markdown("""**Was messen wir?**

**Streaming-Konzentration** = Anteil der Top-5-Tracks am Gesamt-Playcount eines Artists.
Ein hoher Wert (z.B. 80%) bedeutet: Fast alle Streams kommen von 5 Songs — klassisches
"One-Hit-Wonder"-Muster oder sehr enger Fanfokus.
Ein niedriger Wert (z.B. 30%) bedeutet: Streams verteilen sich gleichmäßig über viele Tracks
— ein breiteres, tieferes Katalog-Publikum.

**Tour-Intensität** = Anzahl Events im letzten Jahr (Ticketmaster, letzte 12 Monate).

**Hypothese:** Künstler mit breitem Katalog (niedrige Konzentration) touren intensiver,
weil sie ein loyaleres Stammpublikum haben das regelmäßig wiederkommt. Künstler mit
hoher Konzentration leben von viralen Hits — ihr Live-Publikum ist weniger stabil.
""")

# ── Daten prüfen ───────────────────────────────────────────────────────────
f2_required = ["top5_share", "events_last_year"]
f2_missing = [c for c in f2_required if c not in df.columns]

if f2_missing:
    st.error(f"⚠️  Fehlende Spalten: {f2_missing}")
    st.code("""
# Ausführungsreihenfolge:
python scripts/collect_toptracks.py    # Last.fm Top-Tracks holen
python scripts/join_data.py            # Konzentration berechnen + joinen
    """)
    st.stop()

df2 = df.dropna(subset=["top5_share", "events_last_year"]).copy()
df2["top5_share"] = pd.to_numeric(df2["top5_share"], errors="coerce")
df2["events_last_year"] = pd.to_numeric(df2["events_last_year"], errors="coerce")
df2 = df2.dropna(subset=["top5_share", "events_last_year"])

n_f2 = len(df2)
pct_cov_f2 = n_f2 / len(df) * 100

st.info(f"📊 {n_f2} Artists mit vollständigen F2-Daten ({pct_cov_f2:.0f}% des Datensatzes)")

if n_f2 < 10:
    st.warning("Zu wenig Datenpunkte. Bitte `collect_toptracks.py` ausführen.")
    st.stop()

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F2 — GRAPH 1: Scatterplot top5_share vs events_last_year
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Graph 1 — Scatterplot: Streaming-Konzentration vs. Tour-Intensität</div>',
            unsafe_allow_html=True
            )
st.markdown("""Jeder Punkt = ein Künstler. X-Achse = Top-5-Anteil (Konzentration), Y-Achse =
Events letztes Jahr (Tour-Intensität). Die OLS-Trendlinie zeigt die Richtung
des Zusammenhangs. Hover über Punkte für Artist-Details.""")

sc1, sc2, sc3 = st.columns([2, 1, 1])
with sc1:
    conc_metric = st.radio(
        "Konzentrations-Metrik (X-Achse)",
        ["top5_share", "top3_share", "top1_share", "hhi"],
        index=0,
        horizontal=True,
        key="f2s_metric"
    )
    metric_labels = {
        "top5_share": "Anteil Top-5 Tracks am Gesamt-Playcount (%)",
        "top3_share": "Anteil Top-3 Tracks am Gesamt-Playcount (%)",
        "top1_share": "Anteil Track #1 am Gesamt-Playcount (%)",
        "hhi": "Herfindahl-Index (Konzentrationsmaß 0–10000)",
    }
with sc2:
    log_y_s = st.checkbox("Log Y (Events)", value=False, key="f2s_logy")
    show_names_s = st.checkbox("Namen anzeigen", value=False, key="f2s_names")
with sc3:
    ev_max = st.slider(
        "Max. Events/Jahr",
        5, int(df2["events_last_year"].max()) + 5,
        int(df2["events_last_year"].quantile(0.97)),
        key="f2s_evmax"
    )

sel_genres_f2 = st.multiselect(
    "🎵 Genre-Filter", options=top_genres, default=[], key="f2s_genres"
)

# Metrik prüfen
if conc_metric not in df2.columns:
    st.warning(f"Metrik `{conc_metric}` nicht im Dataset — nur top5_share verfügbar.")
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
    strength_f2 = "stark" if abs(r_f2) >= 0.7 else "moderat" if abs(r_f2) >= 0.4 else "schwach"
    direction_f2 = "negativ" if r_f2 < 0 else "positiv"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("n Artists", len(df2f))
    m2.metric("Pearson r", f"{r_f2:.3f}")
    m3.metric("R²", f"{r2_f2:.1%}")
    m4.metric("p-Wert", f"{p_f2:.4f}",
              delta="signifikant ✅" if p_f2 < 0.05 else "nicht signifikant ⚠️",
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

    # Manuelle OLS-Trendlinie
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
        color_continuous_scale="RdYlGn_r",  # rot=hoch konzentriert, grün=breit
        text="artist_name" if show_names_s else None,
        labels={
            conc_metric: metric_labels.get(conc_metric, conc_metric),
            "y_plot": f"{'log₁₀(' if log_y_s else ''}Events letztes Jahr{')' if log_y_s else ''}",
        },
        title=(
            f"Streaming-Konzentration vs. Tour-Intensität  "
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
        <h4>📊 Statistisches Ergebnis</h4>
        <p>
        Pearson r = <strong style="color:#1DB954">{r_f2:.3f}</strong> →
        <strong>{strength_f2}e {direction_f2}e Korrelation</strong> zwischen
        Streaming-Konzentration und Tour-Intensität.
        R² = <strong style="color:#1DB954">{r2_f2:.1%}</strong>,
        p = {p_f2:.4f} →
        <strong>{"statistisch signifikant ✅" if p_f2 < 0.05 else "nicht signifikant ⚠️"}</strong>.
        </p>
    </div>
    <div class="insight-card">
        <h4>🔍 Interpretation</h4>
        <p>
        {
    f"Künstler mit <strong>niedrigerer Streaming-Konzentration</strong> (Streams verteilen sich breiter) touren intensiver — konsistent mit der Hypothese: ein tiefes Katalog-Publikum trägt die Tour."
    if r_f2 < -0.2 and p_f2 < 0.05 else
    f"Künstler mit <strong>höherer Streaming-Konzentration</strong> touren intensiver — das könnte bedeuten: ein viraler Hit treibt auch mehr Live-Nachfrage."
    if r_f2 > 0.2 and p_f2 < 0.05 else
    "Die Streaming-Konzentration hängt kaum mit der Tour-Intensität zusammen. Beide Dimensionen sind weitgehend unabhängig — weder Katalog-Tiefe noch Hit-Konzentration ist ein verlässlicher Vorhersagefaktor für Touring-Aktivität."
    }
        <br><br>
        <strong>Im Kontext des Gesamtprojekts:</strong>
        Kombiniert mit F1 (Listeners → Skala der Tour) zeigt dieses Ergebnis ob die
        <em>Qualität</em> der Streaming-Aktivität (breit vs. konzentriert) eine andere
        Vorhersagekraft hat als die <em>Quantität</em> (Gesamtlistener).
        </p>
    </div>""", unsafe_allow_html=True)
else:
    st.warning("Zu wenig Datenpunkte nach Filterung.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F2 — GRAPH 2: Boxplot — Events/Jahr nach Konzentrations-Kategorie
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📦 Graph 2 — Tour-Intensität nach Konzentrations-Kategorie (Box Plot)</div>',
            unsafe_allow_html=True
            )
st.markdown("""Künstler werden in **Konzentrations-Kategorien** eingeteilt — von "Breites Repertoire"
(viele Tracks tragen zum Streaming bei) bis "Hochkonzentriert" (wenige Tracks dominieren).
Der **Box Plot** zeigt die Verteilung der Tour-Intensität pro Kategorie und macht
strukturelle Unterschiede sichtbar die im Scatterplot untergehen.""")

bx1, bx2 = st.columns([1, 3])
with bx1:
    n_cats = st.select_slider("Anzahl Kategorien", [3, 4, 5], value=4, key="f2b_nc")
    bx_metric = st.radio("Y-Achse", ["Events letztes Jahr", "Events gesamt"], key="f2b_ym")

df2b = df2.dropna(subset=["top5_share", "events_last_year", "total_events"]).copy()
y_col_bx = "events_last_year" if bx_metric == "Events letztes Jahr" else "total_events"

try:
    cat_labels = {
        3: ["🟢 Breites\nRepertoire", "🟡 Moderat\nkonzentriert", "🔴 Hochkon-\nzentriert"],
        4: ["🟢 Breit", "🟡 Moderat", "🟠 Fokussiert", "🔴 Konzentriert"],
        5: ["🟢 Sehr breit", "🟢 Breit", "🟡 Moderat", "🟠 Fokussiert", "🔴 Konzentriert"],
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
            marker_color=bx_colors[i],  # type: ignore
            line_color=bx_colors[i],  # type: ignore
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
        kw_str = f"Kruskal-Wallis H = {kw_stat:.2f}, p = {kw_p:.4f} → {'signifikant ✅' if kw_p < 0.05 else 'nicht signifikant ⚠️'}"

    fig_bx2.update_layout(
        title=f"Tour-Intensität nach Konzentrations-Kategorie — {bx_metric}",
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
            <h4>📊 Statistischer Test (Kruskal-Wallis)</h4>
            <p>{kw_str}<br>
            <em>Nicht-parametrischer Test — robust bei schiefer Verteilung von Event-Counts.</em></p>
        </div>""", unsafe_allow_html=True)

except Exception as e:
    with bx2:
        st.warning(f"Box Plot Fehler: {e}")

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F2 — GRAPH 3: Top-Track-Konzentration Profil (Beispiel-Artists)
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🎵 Graph 3 — Streaming-Profil: Top Artists im Vergleich</div>', unsafe_allow_html=True)
st.markdown("""Ein **gestapeltes Balkendiagramm** zeigt für ausgewählte Künstler wie sich der
Gesamt-Playcount auf ihre Top-Tracks verteilt. Das macht die Konzentrations-Metrik
anschaulich: Man sieht direkt wer "Ein-Hit-Wonder" ist und wer auf einen
breiten Katalog aufbaut.""")

# Artists für Profilgraph wählen — standardmäßig die 2 extremen + 2 mittlere
if len(df2) >= 4:
    most_conc = df2.nlargest(2, "top5_share")["artist_name"].tolist()
    least_conc = df2.nsmallest(2, "top5_share")["artist_name"].tolist()
    default_sel = most_conc + least_conc
else:
    default_sel = df2["artist_name"].tolist()[:4]

sel_artists = st.multiselect(
    "Artists auswählen (4–8 empfohlen)",
    options=sorted(df2["artist_name"].tolist()),
    default=default_sel[:6],
    key="f2p_artists"
)

if sel_artists and os.path.exists("data/raw/lastfm_toptracks.csv"):
    df_tracks_raw = pd.read_csv("data/raw/lastfm_toptracks.csv")
    df_tracks_sel = df_tracks_raw[df_tracks_raw["artist_name"].isin(sel_artists)].copy()
    df_tracks_sel["playcount"] = pd.to_numeric(df_tracks_sel["playcount"], errors="coerce")

    n_top_show = st.slider("Top N Tracks anzeigen", 3, 10, 5, key="f2p_ntracks")

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
                    f"Anteil: {pct:.1f}%<br>"
                    f"Plays: {int(row['playcount']):,}<extra></extra>"
                ),
                showlegend=(artist == sel_artists[0]),
                legendgroup=f"track_{j}",
            ))

    fig_profile.update_layout(
        barmode="stack",
        title=f"Top-{n_top_show}-Track Anteil am Gesamt-Playcount",
        xaxis_title="Artist",
        yaxis_title="Anteil am Gesamt-Playcount (%)",
        yaxis=dict(range=[0, 100], gridcolor="#333"),
        template="plotly_dark",
        paper_bgcolor="#0e0e0e", plot_bgcolor="#1a1a1a",
        font=dict(color="white"), height=430,
        legend=dict(orientation="h", y=-0.2, font=dict(size=10)),
        xaxis=dict(tickangle=-20)
    )
    st.plotly_chart(fig_profile, use_container_width=True)

    # Tabelle: Konzentration + Events
    tbl_data = df2[df2["artist_name"].isin(sel_artists)][
        ["artist_name", "top5_share", "top3_share", "top1_share", "events_last_year", "total_events"]
    ].sort_values("top5_share", ascending=False)
    tbl_data.columns = ["Artist", "Top-5 %", "Top-3 %", "Top-1 %", "Events/Jahr", "Events gesamt"]
    st.dataframe(tbl_data.set_index("Artist").style.format({
        "Top-5 %": "{:.1f}",
        "Top-3 %": "{:.1f}",
        "Top-1 %": "{:.1f}",
        "Events/Jahr": "{:.0f}",
        "Events gesamt": "{:.0f}",
    }).background_gradient(cmap="RdYlGn_r", subset=["Top-5 %"])
                 .background_gradient(cmap="YlGn", subset=["Events/Jahr"]),
                 use_container_width=True)
else:
    st.info("Keine Artists ausgewählt oder `lastfm_toptracks.csv` fehlt.")

# ── Zusammenfassung F2 ─────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-title">Zusammenfassung — Research Question 2</div>', unsafe_allow_html=True)

if len(df2f) >= 5:
    st.markdown(f"""
    | Metrik | Wert |
    |--------|------|
    | Artists mit vollständigen F2-Daten | {n_f2} ({pct_cov_f2:.0f}%) |
    | Konzentrations-Metrik | Top-5-Track Anteil am Gesamt-Playcount |
    | Tour-Intensität | Events im letzten Jahr (Ticketmaster) |
    | Pearson r | {r_f2:.3f} |
    | R² | {r2_f2:.1%} |
    | p-Wert | {p_f2:.4f} |
    | Signifikant | {'Ja ✅' if p_f2 < 0.05 else 'Nein ⚠️'} |
    """)

    st.markdown(f"""<div class="insight-card">
        <h4>🎯 Antwort auf Research Question 2</h4>
        <p>
        Die Streaming-Konzentration (Top-5-Anteil) zeigt eine
        <strong>{strength_f2}e {direction_f2}e Korrelation</strong>
        (r = {r_f2:.3f}, R² = {r2_f2:.1%}) mit der Tour-Intensität.
        {
    "Das stützt die Hypothese: Künstler mit breitem, gleichmäßig verteiltem Streaming-Profil touren intensiver — ihr Publikum ist loyaler und folgt ihnen auf Tour." if r_f2 < -0.2 and p_f2 < 0.05 else
    "Überraschend: hohe Konzentration geht mit mehr Events einher — mögliche Erklärung: ein viraler Hit erhöht kurzfristig auch die Live-Nachfrage." if r_f2 > 0.2 and p_f2 < 0.05 else
    "Die Konzentration der Streaming-Aktivität ist kein signifikanter Vorhersagefaktor für Tour-Intensität. Die Art der Popularität (breit vs. konzentriert) spielt für die physische Touraktivität keine entscheidende Rolle."
    }
        <br><br>
        <strong>Im Gesamtkontext:</strong> Verglichen mit F1 (Listeners → Events: quantitative
        Größe der Popularität) zeigt F2 dass die <em>Struktur</em> der Streaming-Aktivität
        {"eine ergänzende Vorhersagekraft hat." if p_f2 < 0.05 else "keinen zusätzlichen Erklärungswert bietet."}
        </p>
    </div>""", unsafe_allow_html=True)

st.markdown("""<div class="methodology-note">
    <p>
    <strong>Methodische Anmerkung:</strong>
    Streaming-Konzentration = Anteil der Top-5-Tracks am Gesamt-Playcount
    der von Last.fm zurückgegebenen Top-20-Tracks (<code>artist.getTopTracks</code>).
    Die Metrik unterschätzt leicht die Konzentration falls ein Artist mehr als 20
    relevante Tracks hat. Tour-Intensität = Anzahl Ticketmaster-Events der letzten
    12 Monate (Stichtag März 2026). Ergänzend wurde der Herfindahl-Hirschman Index (HHI)
    als strengeres Konzentrationsmaß berechnet (verfügbar in Graph 1 via Metrik-Auswahl).
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

st.markdown("""**Warum diese Frage?**
Spotify-Charts und Last.fm-Listeners sind zwei unabhängige Popularitäts-Signale
von verschiedenen Plattformen. Wenn Chart-Artists systematisch mehr Last.fm-Listeners haben,
deutet das auf **cross-platform Popularität** hin — digitale Popularität ist plattformübergreifend kohärent.
Wenn nicht, haben die Plattformen unterschiedliche Nutzer-Ökosysteme.

**Hypothese:** Artists die im globalen Spotify Weekly Chart waren, haben signifikant
mehr Last.fm Listeners — weil beide Metriken allgemeine Popularität messen.

**Test-Methode:** Mann-Whitney U (nicht-parametrisch, robust gegenüber den
stark rechtsschiefen Listener-Verteilungen).""")


# ── F3 Daten laden ─────────────────────────────────────────────────────────
@st.cache_data
def load_f3_data():
    p = "data/processed/spotify_charts/chart_artists.csv"
    if not os.path.exists(p):
        return None
    return pd.read_csv(p)


charts_df = load_f3_data()

if charts_df is None:
    st.error("⚠️  `data/processed/spotify_charts/chart_artists.csv` fehlt.")
    st.code("python scripts/process_spotify_charts.py", language="bash")
    st.stop()

# Join: was_on_chart
charts_df["artist_norm"] = charts_df["artist"].str.lower().str.strip()
df3 = df.copy()
df3["artist_norm"] = df3["artist_name"].str.lower().str.strip()
df3["was_on_chart"] = df3["artist_norm"].isin(set(charts_df["artist_norm"]))

# Chart-Metriken joinen
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
k1.metric("Chart Artists", n_chart, delta=f"{n_chart / (n_chart + n_non_chart) * 100:.0f}% des Datasets")
k2.metric("Non-Chart Artists", n_non_chart)
k3.metric("Ø Listeners Chart", f"{mean_c:,.0f}")
k4.metric("Ø Listeners Non-Chart", f"{mean_nc:,.0f}")
k5.metric("Ratio", f"{ratio:.1f}×",
          delta="Chart höher" if ratio > 1 else "kein Unterschied",
          delta_color="normal" if ratio > 1 else "off")
st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F3 — GRAPH 1: Box / Violin Plot — Listeners nach Chart-Status
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📦 Graph 1 — Listener-Verteilung: Chart vs. Non-Chart</div>', unsafe_allow_html=True)
st.markdown("""Der **Box Plot** zeigt Median, Quartile und Ausreißer für beide Gruppen im direkten Vergleich.""")

g1, g2 = st.columns([1, 3])
with g1:
    show_pts = st.checkbox("Punkte anzeigen", value=True, key="f3_pts")

df3_plot = df3.copy()
df3_plot["Gruppe"] = df3_plot["was_on_chart"].map(
    {True: "✅ Im Spotify Chart", False: "❌ Nicht im Chart"}
)
df3_plot["listeners_plot"] = df3_plot["listeners"]
grp_order = ["❌ Nicht im Chart", "✅ Im Spotify Chart"]

COLORS_F3 = {
    "✅ Im Spotify Chart": ("#6366f1", "rgba(99,102,241,0.2)"),
    "❌ Nicht im Chart": ("#94a3b8", "rgba(148,163,184,0.15)"),
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
    title="Last.fm Listeners — Chart vs. Non-Chart Artists",
    xaxis_title="Last.fm Listeners",
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
    eff_lbl2 = ("groß" if abs(cohens_d2) >= 0.8 else
                "mittel" if abs(cohens_d2) >= 0.5 else
                "klein" if abs(cohens_d2) >= 0.2 else "vernachlässigbar")

    st.markdown(f"""<div class="insight-card">
        <h4>📊 Statistische Tests</h4>
        <p>
        <strong>Mann-Whitney U</strong> = {u_stat:.0f} &nbsp;|&nbsp;
        p = <strong style="color:#818cf8">{u_p:.4f}</strong> &nbsp;→&nbsp;
        <strong>{"Signifikant ✅" if u_p < 0.05 else "Nicht signifikant ⚠️"}</strong>
        <br>
        Welch's t-Test (log): t = {t_stat2:.3f} &nbsp;|&nbsp; p = {t_p2:.4f}
        <br>
        Cohen's d = {cohens_d2:.3f} → <strong>{eff_lbl2}e Effektstärke</strong>
        <br><br>
        Chart Artists haben Ø <strong style="color:#6366f1">{ratio:.1f}×</strong> mehr Last.fm Listeners.
        {
    " Die Popularitäts-Niveaus sind plattformübergreifend konsistent — wer auf Spotify chartet, hat auch auf Last.fm eine größere Hörerschaft." if u_p < 0.05 and ratio > 1
    else " Kein signifikanter Unterschied — Spotify-Charts und Last.fm-Listeners messen teilweise unterschiedliche Nutzer-Ökosysteme."
    }
        </p>
    </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════════════════
# F3 — GRAPH 2: Histogram overlay — Listener-Verteilung beider Gruppen
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Graph 2 — Verteilung der Listeners (Überlagerung)</div>', unsafe_allow_html=True)
st.markdown("""Überlagertes Histogramm beider Gruppen auf log-Skala.
Die Verschiebung der Chart-Verteilung nach rechts visualisiert den Listener-Vorsprung.""")

h1, h2 = st.columns([1, 3])
with h1:
    n_bins_f3 = st.slider("Bins", 15, 60, 30, key="f3_bins")
    norm_hist = st.checkbox("Normiert (Dichte)", value=True, key="f3_norm")

hist_mode = "probability density" if norm_hist else ""

fig_f3g2 = go.Figure()
for grp, col in [("❌ Nicht im Chart", "#94a3b8"), ("✅ Im Spotify Chart", "#6366f1")]:
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
    title="Listener-Verteilung — Chart vs. Non-Chart",
    xaxis_title="Last.fm Listeners",
    yaxis_title="Dichte" if norm_hist else "Anzahl Artists",
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
    st.markdown('<div class="section-title">📈 Graph 3 — Chart-Intensität vs. Last.fm Listeners</div>',
                unsafe_allow_html=True)
    st.markdown("Nur Chart-Artists. Je länger ein Artist im Spotify-Chart war, desto mehr Last.fm-Listeners? " +
                tt("OLS", "OLS-Trendlinie") + " zeigt den Zusammenhang.", unsafe_allow_html=True)

    s1, s2 = st.columns([1, 3])
    with s1:
        x_metric_f3 = st.radio("X-Achse",
                               ["chart_weeks", "total_chart_streams"],
                               index=0, key="f3_x",
                               format_func=lambda x: {"chart_weeks": "Wochen im Chart",
                                                      "total_chart_streams": "Gesamt-Streams"}[x])
        log_y_f3 = st.checkbox("Log Y", value=True, key="f3_logy")
        lbl_f3 = st.checkbox("Namen", value=False, key="f3_lbl")

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
        m1f3.metric("n Chart Artists", len(df_sc3))
        m2f3.metric("Pearson r", f"{r_f3:.3f}")
        m3f3.metric("p-Wert", f"{p_f3:.4f}",
                    delta="signifikant ✅" if p_f3 < 0.05 else "nicht signifikant ⚠️",
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
                "y_plot": "log₁₀(Last.fm Listeners)" if log_y_f3 else "Last.fm Listeners",
            },
            title=f"Chart-Intensität vs. Listeners  |  r = {r_f3:.3f}  |  n = {len(df_sc3)}",
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
# F3 — Zusammenfassung
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">Zusammenfassung — Research Question 3</div>', unsafe_allow_html=True)

st.markdown(f"""| Metrik | Wert |
|--------|------|
| Chart Artists (Feb 2023–Feb 2026) | {n_chart} ({n_chart / (n_chart + n_non_chart) * 100:.0f}%) |
| Non-Chart Artists | {n_non_chart} |
| Ø Listeners Chart Artists | {mean_c:,.0f} |
| Ø Listeners Non-Chart Artists | {mean_nc:,.0f} |
| Ratio | {ratio:.1f}× |
| Mann-Whitney U p-Wert | {f"{u_p:.4f}" if u_p is not None else "n/a"} |
| Signifikant (α=0.05) | {"Ja ✅" if u_p is not None and u_p < 0.05 else "Nein ⚠️"} |""")

if u_p is not None:
    st.markdown(f"""<div class="insight-card">
        <h4>🎯 Antwort auf Research Question 3</h4>
        <p>
        Artists die zwischen Feb 2023 und Feb 2026 im globalen Spotify Weekly Chart erschienen,
        haben Ø <strong style="color:#818cf8">{ratio:.1f}×</strong> mehr Last.fm Listeners
        ({mean_c:,.0f} vs. {mean_nc:,.0f}).
        <br><br>
        Der Unterschied ist <strong>{"statistisch signifikant ✅" if u_p < 0.05 else "nicht signifikant ⚠️"}</strong>
        (Mann-Whitney U, p = {u_p:.4f}).
        {
    " Das stützt die Hypothese: digitale Popularität ist plattformübergreifend kohärent — Spotify-Charterfolg und Last.fm-Hörerschaft messen dasselbe Konstrukt aus unterschiedlichen Blickwinkeln." if u_p < 0.05
    else " Das widerlegt die Hypothese: Spotify-Charts und Last.fm-Listeners messen unterschiedliche Fanbasen — die Plattform-Ökosysteme sind nur schwach gekoppelt."
    }
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""<div class="methodology-note">
    <p>
    Chart-Zuordnung über Normalisierung der Künstlernamen (lowercase, trimmed).
    Bei Kollaborationen wird jeder beteiligte Artist einzeln gezählt.
    Zeitraum: 1. Februar 2023 – 28. Februar 2026 (globale Spotify Weekly Charts).
    Last.fm Listener-Counts: Stand März 2026 (aktuell zum Zeitpunkt der Datenerhebung).
    Mann-Whitney U bevorzugt gegenüber t-Test da Listener-Verteilungen stark rechtsschief sind.
    </p>
</div>
""", unsafe_allow_html=True)
