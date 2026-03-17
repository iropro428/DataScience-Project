"""
components/glossary.py
Glossary + CSS tooltips for all technical terms.
"""
import streamlit as st

TERMS = {

    # ── STATISTICS ────────────────────────────────────────────────────────
    "Trend Line": {
        "kurz": "A straight line showing the overall direction of a relationship in a scatterplot",
        "lang": """
**Trend line** is the straight line that best fits all the data points in a scatterplot.

- **Rising line** → positive relationship: as x increases, y tends to increase
- **Falling line** → negative relationship: as x increases, y tends to decrease
- **Flat line** → no relationship: x and y move independently

In this project, trend lines are calculated using Ordinary Least Squares (OLS) — the standard method for finding the best-fit straight line through a set of points.
""",
        "emoji": "📈", "kategorie": "Statistics",
    },

    "Median": {
        "kurz": "The middle value — 50% of values are below it, 50% are above it",
        "lang": """
**Median** is the value exactly in the middle when all values are sorted in order.

It is more robust than the mean (average) when data is skewed — for example, if one artist has 50 million listeners and everyone else has under 2 million, the mean is pulled upward dramatically, but the median barely moves.

In this project, medians are used wherever listener counts or event counts are highly skewed.
""",
        "emoji": "📍", "kategorie": "Statistics",
    },

    "Quartile": {
        "kurz": "Divides data into 4 equally sized groups of 25% each",
        "lang": """
**Quartiles** split all values into four equally sized groups:

- **Q1** = bottom 25% (lowest values)
- **Q2** = 25–50% (below median)
- **Q3** = 50–75% (above median)
- **Q4** = top 25% (highest values)

In this project, artists are grouped into popularity tiers Q1–Q4 based on their Last.fm listener count.
""",
        "emoji": "📦", "kategorie": "Statistics",
    },

    "n": {
        "kurz": "Number of data points included in an analysis",
        "lang": """
**n** = sample size — how many artists, cities, or data points are included in a given calculation.

A larger n makes results more reliable. A small n means even strong-looking patterns should be interpreted cautiously.

In this project, n is shown in chart titles so you always know how many artists a result is based on.
""",
        "emoji": "🔢", "kategorie": "Statistics",
    },

    "Log Scale": {
        "kurz": "A scale where equal steps represent equal multiplications (×10, ×100...)",
        "lang": """
**Log scale** (logarithmic scale) is used when data spans a very wide range of values — for example, Last.fm listener counts range from about 10,000 to over 50 million.

On a normal scale, all the smaller artists would be squished into one tiny corner of the chart. On a log scale, each step represents a ×10 increase, so every artist is visible.

The x-axis label `log₁₀(listeners)` means the displayed value is the base-10 logarithm of the actual listener count. For example: log₁₀(1,000,000) = 6.
""",
        "emoji": "📐", "kategorie": "Statistics",
    },

    # ── METRICS ───────────────────────────────────────────────────────────
    "pct_capital": {
        "kurz": "Share of an artist's total concerts held in capital cities (%)",
        "lang": """
**pct_capital** = (events in capital cities) / (all events) × 100

An artist who plays 10 concerts, 3 of which are in capitals (e.g. Berlin, Paris, London), has a pct_capital of 30%.

This metric counts every performance — so playing 5 shows in Berlin counts as 5 capital events.
""",
        "emoji": "🏛️", "kategorie": "Metrics",
    },

    "pct_capital_cities": {
        "kurz": "Share of the distinct cities an artist visited that are capitals (%)",
        "lang": """
**pct_capital_cities** counts cities, not events. Each city counts only once regardless of how many shows were played there.

An artist who visited London (capital), Manchester, and Berlin (capital) has a pct_capital_cities of 2/3 = 67%.

This can tell a very different story from pct_capital. An artist with 10 shows in London and 1 in Hamburg has pct_capital = 91% (events), but pct_capital_cities = 50% (cities).
""",
        "emoji": "🗺️", "kategorie": "Metrics",
    },

    "Revisit Rate": {
        "kurz": "Share of cities an artist visited more than once on tour (%)",
        "lang": """
**Revisit Rate** = (cities with 2+ visits) / (all cities visited) × 100

A high revisit rate means the artist returns to proven markets — a consolidation strategy.
A low revisit rate means the artist is constantly exploring new cities — a geographic expansion strategy.

In this project, a "revisit city" is any city where an artist has two or more Ticketmaster events recorded between 2023 and 2026.
""",
        "emoji": "🔄", "kategorie": "Metrics",
    },

    "Revisit Ratio": {
        "kurz": "Number of revisit cities divided by number of new cities",
        "lang": """
**Revisit Ratio** = revisit cities / new cities

- **Ratio > 1** → more revisits than new cities (consolidation dominates)
- **Ratio = 1** → equal number of revisits and new cities
- **Ratio < 1** → more new cities than revisits (expansion dominates)

A global ratio of 0.16 means that for every new city added to a tour, only 0.16 cities are revisited — expansion is the dominant pattern.
""",
        "emoji": "📊", "kategorie": "Metrics",
    },

    "Top-5-Share": {
        "kurz": "Share of an artist's total play count coming from their top 5 tracks (%)",
        "lang": """
**Top-5-Share** = (plays of top 5 tracks) / (total plays across top 20 tracks) × 100

A high Top-5-Share (e.g. 90%) means the audience almost exclusively listens to a handful of songs — a one-hit-wonder profile.
A low Top-5-Share (e.g. 30%) means plays are spread broadly across many tracks — a deep-catalogue artist.

This metric is used in Research Question 2 of Streaming & Ticket Power to examine whether streaming concentration relates to tour scale.
""",
        "emoji": "🎧", "kategorie": "Metrics",
    },

    "Lead Time": {
        "kurz": "Number of days between when tickets go on sale and the first concert date",
        "lang": """
**Lead time** measures how far in advance a concert is announced and put on sale.

A lead time of 90 days means tickets went on sale about 3 months before the show.

Longer lead times may reflect larger productions, more complex logistics, or longer marketing campaigns. In this project, only lead times between 0 and 1095 days (3 years) are included to remove implausible values.
""",
        "emoji": "📅", "kategorie": "Metrics",
    },

    "Weekend Share": {
        "kurz": "Share of an artist's concerts that take place on Friday, Saturday, or Sunday (%)",
        "lang": """
**Weekend share** = (concerts on Fri/Sat/Sun) / (all concerts) × 100

A weekend share of 60% means 60% of all concerts happen on weekends. Weekends are typically more attractive for live events because more people are free and ticket demand tends to be higher.

In this project, Friday, Saturday, and Sunday are all counted as weekend days.
""",
        "emoji": "🗓️", "kategorie": "Metrics",
    },

    "Avg. Days Between Shows": {
        "kurz": "Average number of days between consecutive concerts for one artist",
        "lang": """
**Average days between shows** is calculated by taking the dates of all an artist's concerts, computing the gap between each consecutive pair, and averaging those gaps.

A value of 7 means the artist plays roughly once a week on average.
A value of 30 means roughly once a month.

Very short gaps suggest intensive touring; very long gaps may indicate infrequent live activity or long breaks between tours.
""",
        "emoji": "⏱️", "kategorie": "Metrics",
    },

    "Weighted Coverage": {
        "kurz": "Share of an artist's global listener reach that is covered by their tour countries",
        "lang": """
**Weighted Coverage** is the main geo-alignment metric in this project.

Unlike Jaccard, it weights each country by how many listeners the artist has there — so a large listener market that is not toured has a bigger negative impact on the score than a small market.

| Score | Meaning |
|-------|---------|
| **1.0** | The artist tours in every country where they have significant listeners |
| **0.5** | 50% of their total listener reach is covered by their tour countries |
| **0.0** | None of the countries where they have listeners are toured |
""",
        "emoji": "🌍", "kategorie": "Metrics",
    },

    "Tour Coverage": {
        "kurz": "Share of an artist's tour countries that are also top streaming countries (%)",
        "lang": """
**Tour Coverage** answers: of all the countries an artist tours in, how many are also countries where they have a significant streaming presence?

- **High Tour Coverage** → the artist mainly performs where fans already exist
- **Low Tour Coverage** → the artist tours heavily into markets with little prior streaming presence, suggesting a strategy of building new audiences
""",
        "emoji": "🗺️", "kategorie": "Metrics",
    },

    "Streaming Reach": {
        "kurz": "Share of an artist's top streaming countries that are actually visited on tour (%)",
        "lang": """
**Streaming Reach** answers: of all the countries where an artist has significant listeners, how many are actually visited on tour?

- **High Streaming Reach** → the artist converts their digital audience into live shows effectively
- **Low Streaming Reach** → many listener markets are never reached by live performances — these are untapped markets

This is a key metric for answering Research Question 3: how well does touring geography follow streaming geography?
""",
        "emoji": "📡", "kategorie": "Metrics",
    },

    "Geo-Alignment": {
        "kurz": "How well an artist's tour geography matches where their streaming audience is located",
        "lang": """
**Geo-Alignment** is the central concept of Research Question 3 in Geographic Analysis.

A perfectly aligned artist performs in the same countries where their digital fanbase is strongest.
A misaligned artist either:
- Tours regionally despite having a global fanbase (digital reach far exceeds live presence), or
- Tours globally into countries where they have little streaming presence (building new audiences)

Measured using three complementary metrics: Weighted Coverage, Tour Coverage, and Streaming Reach.
""",
        "emoji": "🧭", "kategorie": "Metrics",
    },

}

# ── CSS for tooltips ───────────────────────────────────────────────────────
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
    st.markdown(TOOLTIP_CSS, unsafe_allow_html=True)


def tt(term: str, label: str = None) -> str:
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
    kategorien = {}
    for term, t in TERMS.items():
        k = t.get("kategorie", "Other")
        kategorien.setdefault(k, []).append(term)

    kat_icons = {
        "Statistics": "📊",
        "Metrics": "📏",
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
