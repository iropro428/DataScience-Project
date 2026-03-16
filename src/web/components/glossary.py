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
    "Median": {
        "kurz": "Middle value — 50% of values are below, 50% above",
        "lang": """
**Median** is the value exactly in the middle of a sorted list.

More robust than the mean for skewed data — one superstar artist barely shifts
the median, but can heavily distort the average.
""",
        "emoji": "📍", "kategorie": "Statistics",
    },
    "Quartile": {
        "kurz": "Divides data into 4 equally sized groups (25% each)",
        "lang": """
**Quartiles:** Q1 = bottom 25% · Q2 = 50% · Q3 = 75% · Q4 = top 25%

Used in this project to group artists into popularity tiers.
""",
        "emoji": "📦", "kategorie": "Statistics",
    },
    "n": {
        "kurz": "Number of data points in the analysis",
        "lang": """
**n** = sample size.

Large n → more reliable; even small effects can become significant.
Small n → requires stronger effects to reach significance.
""",
        "emoji": "🔢", "kategorie": "Statistics",
    },
    "Top-5-Share": {
        "kurz": "Share of the top 5 tracks in total play count (%)",
        "lang": """
**Top-5-Share** = What percentage of all streams come from the 5 most-played tracks?

90% → very concentrated (one-hit-wonder effect)
30% → broad catalogue
""",
        "emoji": "🎧", "kategorie": "Metrics",
    },
    "pct_capital": {
        "kurz": "Share of concerts held in capital cities (%)",
        "lang": """
**pct_capital** = Concerts in capital cities / All concerts × 100

Capital cities tend to offer larger venues, more media coverage, and denser fanbases.
""",
        "emoji": "🏛️", "kategorie": "Metrics",
    },
    "Revisit Rate": {
        "kurz": "Share of cities visited more than once on a tour (%)",
        "lang": """
**Revisit Rate** = Cities with 2 or more visits / All cities × 100

High revisit rate → strong local fanbases, consolidation strategy.
Low revisit rate → expansion strategy, reaching new markets.
""",
        "emoji": "🔄", "kategorie": "Metrics",
    },
    "Weighted Coverage": {
        "kurz": "Share of an artist's global listener reach covered by their tour countries",
        "lang": """
**Weighted Coverage** is the main geo-alignment metric in this project.

Unlike Jaccard, it weights each country by how many listeners the artist has there.

| Score | Meaning |
|-------|---------|
| **1.0** | The artist performs in every country where they have significant listeners |
| **0.0** | The artist tours in none of the countries where they have listeners |

A score of 0.6 means 60% of the artist's total listener reach is covered by their tour.
""",
        "emoji": "🌍", "kategorie": "Metrics",
    },
    "Tour Coverage": {
        "kurz": "Share of tour countries that are also top streaming countries (%)",
        "lang": """
**Tour Coverage** answers: of all the countries an artist tours in,
how many are also countries where they have a significant streaming presence?

High Tour Coverage → the artist mainly tours where fans already exist.
Low Tour Coverage → the artist tours heavily into markets without an established audience.
""",
        "emoji": "🗺️", "kategorie": "Metrics",
    },
    "Streaming Reach": {
        "kurz": "Share of streaming countries that are actually toured (%)",
        "lang": """
**Streaming Reach** answers: of all the countries where an artist has significant listeners,
how many are actually visited on tour?

High Streaming Reach → the artist converts their digital presence into live shows effectively.
Low Streaming Reach → many listener markets remain unreached by live performances.
""",
        "emoji": "📡", "kategorie": "Metrics",
    },
    "Geo-Alignment": {
        "kurz": "How well an artist's tour geography matches their streaming audience geography",
        "lang": """
**Geo-Alignment** is the central concept of Research Question 3.

It measures whether artists perform in the same countries where their digital fanbase is located.
A perfectly aligned artist tours exactly where their listeners are.
A misaligned artist either tours regionally despite a global fanbase,
or tours globally into markets where they have little streaming presence.

Measured using three metrics: Jaccard Similarity, Weighted Coverage, and Streaming Reach.
""",
        "emoji": "🧭", "kategorie": "Metrics",
    },
    "Scatterplot": {
        "kurz": "Chart where each dot is one artist — X and Y are two measured values",
        "lang": """
**Scatterplot** shows the relationship between two variables.

Points aligned along a line → relationship exists.
Randomly distributed → no relationship.
The OLS line shows the average trend across all artists.
""",
        "emoji": "🔵", "kategorie": "Visualisation",
    },
    "Box Plot": {
        "kurz": "Shows minimum, maximum, median and spread of a group in one compact chart",
        "lang": """
**Box Plot** displays 5 key values:

- Box = middle 50% of the data (Q1 to Q3)
- Line inside box = median
- Whiskers = range excluding extreme outliers
- Dots outside = outliers
""",
        "emoji": "📦", "kategorie": "Visualisation",
    },
    "Log Scale": {
        "kurz": "Scale where equal distances represent equal ratios (×10, ×100...)",
        "lang": """
**Log Scale** solves the problem when data spans very different orders of magnitude
(e.g. 100k to 50 million listeners).

Each step = ×10. This makes all artists visible in one chart — not just the superstars.
""",
        "emoji": "📐", "kategorie": "Visualisation",
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
    """Complete glossary page — all terms grouped by category."""
    kategorien = {}
    for term, t in TERMS.items():
        k = t.get("kategorie", "Other")
        kategorien.setdefault(k, []).append(term)

    kat_icons = {
        "Statistics": "📊",
        "Metrics": "📏",
        "Visualisation": "🎨",
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
