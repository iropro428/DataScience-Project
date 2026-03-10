"""
components/glossary.py
Glossar + CSS-Tooltips fuer alle Fachbegriffe.

Verwendung:
    from components.glossary import apply_glossary_styles, tt, glossar_seite
    apply_glossary_styles()   # einmal pro Page aufrufen
    st.markdown("Der " + tt("Pearson r") + " beträgt 0.21", unsafe_allow_html=True)
"""
import streamlit as st

TERMS = {
    "Pearson r": {
        "kurz": "Stärke des Zusammenhangs zwischen zwei Variablen (-1 bis +1)",
        "lang": """
**Pearson r** misst wie stark zwei Zahlen zusammenhängen.

| Wert | Bedeutung |
|------|-----------|
| **+1** | Steigt X → steigt Y immer mit |
| **0** | Kein Zusammenhang |
| **-1** | Steigt X → fällt Y immer |

**Faustregel:** < 0.2 = vernachlässigbar · 0.2–0.4 = schwach · 0.4–0.7 = moderat · > 0.7 = stark
""",
        "emoji": "📏", "kategorie": "Statistik",
    },
    "p-Wert": {
        "kurz": "Wahrscheinlichkeit dass das Ergebnis reiner Zufall ist (< 0.05 = signifikant)",
        "lang": """
**p-Wert** beantwortet: *Koennte dieses Ergebnis reiner Zufall sein?*

| p-Wert | Bedeutung |
|--------|-----------|
| **< 0.05** | Signifikant — sehr unwahrscheinlich Zufall |
| **0.05–0.10** | Schwacher Hinweis |
| **> 0.10** | Kein belastbares Ergebnis |

p = 0.0109 bedeutet: nur 1.09% Wahrscheinlichkeit dass der Zusammenhang Zufall ist.
""",
        "emoji": "🎯", "kategorie": "Statistik",
    },
    "R²": {
        "kurz": "Wie viel Prozent der Variation erklärt das Modell? (0-100%)",
        "lang": """
**R²** = Pearson r zum Quadrat.

Sagt wie viel Prozent der Unterschiede zwischen Artists die X-Variable erklärt.

r = 0.21 → R² = 4.4% → Nur 4.4% der Listener-Unterschiede erklärt durch Chart-Wochen.
""",
        "emoji": "📐", "kategorie": "Statistik",
    },
    "OLS": {
        "kurz": "Trendlinie die am besten durch alle Punkte passt (Methode der kleinsten Quadrate)",
        "lang": """
**OLS** = Ordinary Least Squares.

Berechnet automatisch die gerade Linie die durchschnittlich am nächsten an allen Punkten liegt.

- Linie steigt → positiver Zusammenhang
- Linie fällt → negativer Zusammenhang
- Flache Linie → kein Zusammenhang
""",
        "emoji": "📈", "kategorie": "Statistik",
    },
    "Mann-Whitney U": {
        "kurz": "Vergleicht zwei Gruppen ohne Annahmen ueber die Verteilung",
        "lang": """
**Mann-Whitney U** vergleicht zwei Gruppen — robust bei schiefen Verteilungen.

Warum nicht t-Test? Listener-Zahlen sind extrem schief (Taylor Swift vs. Indie-Artist).
Mann-Whitney sortiert alle Artists nach Listeners und prueft ob Chart-Artists
systematisch weiter oben stehen.
""",
        "emoji": "⚖️", "kategorie": "Statistik",
    },
    "Kruskal-Wallis": {
        "kurz": "Vergleicht 3 oder mehr Gruppen — Erweiterung von Mann-Whitney",
        "lang": """
**Kruskal-Wallis** wie Mann-Whitney U, aber fuer 3+ Gruppen.

H-Statistik: je groesser, desto mehr unterscheiden sich die Gruppen.
p-Wert < 0.05 → mindestens zwei Gruppen unterscheiden sich signifikant.
""",
        "emoji": "📊", "kategorie": "Statistik",
    },
    "Cohen's d": {
        "kurz": "Wie gross ist der Unterschied zwischen zwei Gruppen wirklich?",
        "lang": """
**Cohen's d** misst die praktische Bedeutung — unabhängig von Signifikanz.

| d | Effektstärke |
|---|--------------|
| < 0.2 | Vernachlässigbar |
| 0.2–0.5 | Klein |
| 0.5–0.8 | Mittel |
| > 0.8 | Gross |
""",
        "emoji": "📏", "kategorie": "Statistik",
    },
    "Signifikant": {
        "kurz": "Ergebnis ist sehr wahrscheinlich kein Zufall (p < 0.05)",
        "lang": """
**Statistisch signifikant** = das Muster wuerde bei zufälligen Daten
nur in weniger als 5% der Fälle auftreten.

Wichtig: Signifikant ≠ wichtig oder gross — nur 'nicht zufällig'.
""",
        "emoji": "✅", "kategorie": "Statistik",
    },
    "Median": {
        "kurz": "Mittlerer Wert — 50% liegen darunter, 50% darueber",
        "lang": """
**Median** ist der Wert genau in der Mitte (sortierte Reihe).

Robuster als Mittelwert bei schiefen Daten — Taylor Swift verfälscht
den Durchschnitt, den Median kaum.
""",
        "emoji": "📍", "kategorie": "Statistik",
    },
    "Quartil": {
        "kurz": "Teilt Daten in 4 gleich grosse Gruppen (je 25%)",
        "lang": """
**Quartile:** Q1 = untere 25% · Q2 = 50% · Q3 = 75% · Q4 = obere 25%

Verwendung: Artists nach Popularity-Tier gruppieren.
""",
        "emoji": "📦", "kategorie": "Statistik",
    },
    "n": {
        "kurz": "Anzahl der Datenpunkte in der Analyse",
        "lang": """
**n** = Stichprobengroesse.

Grosses n → zuverlässiger, auch kleine Effekte werden signifikant.
Kleines n → braucht stärkere Effekte um signifikant zu werden.
""",
        "emoji": "🔢", "kategorie": "Statistik",
    },
    "HHI": {
        "kurz": "Misst wie konzentriert Streams auf wenige Top-Tracks sind (0-10.000)",
        "lang": """
**HHI** = Herfindahl-Hirschman Index.

Nah 0 → Streams gleichmässig verteilt (breiter Katalog)
Nah 10.000 → Fast alles von einem Track (One-Hit-Wonder)
""",
        "emoji": "🎵", "kategorie": "Metriken",
    },
    "Top-5-Share": {
        "kurz": "Anteil der Top-5-Tracks am Gesamt-Playcount (%)",
        "lang": """
**Top-5-Share** = Wie viel % aller Streams kommen von den 5 meistgehoerten Tracks?

90% → sehr konzentriert (One-Hit-Wonder-Effekt)
30% → breiter Katalog
""",
        "emoji": "🎧", "kategorie": "Metriken",
    },
    "pct_capital": {
        "kurz": "Anteil der Konzerte in Hauptstädten (%)",
        "lang": """
**pct_capital** = Konzerte in Hauptstädten / Alle Konzerte × 100

Hauptstädte bieten groessere Venues, mehr Presse, dichtere Fanbase.
""",
        "emoji": "🏛️", "kategorie": "Metriken",
    },
    "pct_revisit": {
        "kurz": "Anteil der Städte die ein Artist mehr als einmal besucht (%)",
        "lang": """
**pct_revisit_cities** = Städte mit ≥ 2 Besuchen / Alle Städte × 100

Hoch → starke lokale Fanbasen · Niedrig → Expansions-Strategie
""",
        "emoji": "🔄", "kategorie": "Metriken",
    },
    "Scatterplot": {
        "kurz": "Diagramm wo jeder Punkt ein Artist ist — X und Y sind zwei Messwerte",
        "lang": """
**Scatterplot** zeigt den Zusammenhang zwischen zwei Variablen.

Punkte auf einer Linie → Zusammenhang.
Zufällig verteilt → kein Zusammenhang.
OLS-Linie zeigt den Durchschnittstrend.
""",
        "emoji": "🔵", "kategorie": "Visualisierung",
    },
    "Box Plot": {
        "kurz": "Zeigt Minimum, Maximum, Median und Streuung einer Gruppe kompakt",
        "lang": """
**Box Plot** zeigt 5 Kennzahlen:

- Box = mittlere 50% der Daten (Q1 bis Q3)
- Linie in Box = Median
- Striche = Bereich ohne extreme Ausreisser
- Punkte aussen = Ausreisser
""",
        "emoji": "📦", "kategorie": "Visualisierung",
    },
    "Log-Skala": {
        "kurz": "Skala wo gleiche Abstände gleiche Verhältnisse bedeuten (x10, x100...)",
        "lang": """
**Log-Skala** loest das Problem wenn Daten sehr unterschiedliche
Groessenordnungen haben (100k bis 50 Mio Listeners).

Jeder Schritt = x10. So werden alle Artists sichtbar — nicht nur die Superstars.
""",
        "emoji": "📐", "kategorie": "Visualisierung",
    },
}

# ── CSS fuer schoene Tooltips ──────────────────────────────────────────────
TOOLTIP_CSS = """
<style>
.gt {
    position: relative;
    display: inline-block;
    border-bottom: 1px dashed #6366f1;
    color: #818cf8 !important;
    cursor: help;
    font-weight: 500;
}
.gt .gt-box {
    visibility: hidden;
    opacity: 0;
    width: 280px;
    background: #1d2440;
    border: 1px solid #2e3557;
    border-left: 3px solid #6366f1;
    border-radius: 10px;
    padding: 10px 14px;
    position: absolute;
    z-index: 9999;
    bottom: 130%;
    left: 50%;
    transform: translateX(-50%);
    transition: opacity 0.18s ease;
    pointer-events: none;
    box-shadow: 0 8px 32px rgba(0,0,0,0.6);
}
.gt .gt-box::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: #2e3557;
}
.gt:hover .gt-box {
    visibility: visible;
    opacity: 1;
}
.gt-emoji {
    font-size: 1rem;
    margin-right: 4px;
}
.gt-term {
    font-weight: 700;
    font-size: 0.82rem;
    color: #818cf8 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    display: block;
    margin-bottom: 4px;
}
.gt-def {
    font-size: 0.82rem;
    color: #94a3b8 !important;
    line-height: 1.5;
}
</style>
"""


def apply_glossary_styles():
    """Einmal pro Page aufrufen — injiziert Tooltip-CSS."""
    st.markdown(TOOLTIP_CSS, unsafe_allow_html=True)


def tt(term: str, label: str = None) -> str:
    """
    Gibt HTML-Tooltip-Span zurueck.
    Verwendung: st.markdown("Der " + tt("Pearson r") + " = 0.21", unsafe_allow_html=True)
    """
    if term not in TERMS:
        return label or term
    t = TERMS[term]
    display = label or term
    kurz = t["kurz"].replace("<", "&lt;").replace(">", "&gt;")
    return (
        f'<span class="gt">{display}'
        f'<span class="gt-box">'
        f'<span class="gt-term">{t["emoji"]} {term}</span>'
        f'<span class="gt-def">{kurz}</span>'
        f'</span></span>'
    )


def glossar_seite():
    """Vollständige Glossar-Seite — alle Begriffe nach Kategorie."""
    kategorien = {}
    for term, t in TERMS.items():
        k = t.get("kategorie", "Sonstiges")
        kategorien.setdefault(k, []).append(term)

    kat_icons = {
        "Statistik": "📊",
        "Metriken": "📏",
        "Visualisierung": "🎨",
    }

    for kat, terms in kategorien.items():
        icon = kat_icons.get(kat, "📌")
        st.markdown(f"### {icon} {kat}")
        cols = st.columns(2)
        for i, term in enumerate(terms):
            t = TERMS[term]
            with cols[i % 2]:
                with st.expander(t["emoji"] + " " + term + " — " + t["kurz"]):
                    st.markdown(t["lang"])
        st.divider()
