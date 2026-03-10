# Live Music: Digital Popularity vs Reality

# From Streams to Stages  
To what extent do digital Spotify metrics predict the physical reality of global concert tours?

---

# Project Overview

This project examines whether digital streaming indicators — particularly Spotify popularity metrics — can predict measurable real-world outcomes in live music performance.

We aim to bridge the gap between:

- Digital popularity (streams, followers, popularity scores)
- Physical concert performance (ticket availability, scheduling, geographic reach)

The project integrates multiple APIs to construct a structured, reproducible data pipeline for cross-platform analysis.

---

# Research Questions

1. Streaming & Ticket Power

- How does the number of Last.fm listeners correlate with the scale of an artist's tour, measured by the number of events scheduled?
- How does the concentration of an artist's streaming activity on a few top tracks relate to the intensity of their touring, measured by events per year?
- How do current Last.fm listener counts differ between artists who appeared in Spotify Weekly Charts between February 2023 and February 2026 and those who did not?


2. Geographic Analysis

- What is the ratio of revisit cities to new cities on an artist's current tour?
- What proportion of an artist's performances take place in capital cities compares to non-capital cities?
- How well do the countries where an artist has the highest listener reach on Last.fm align with the countries where they perform on their Ticketmaster tour?


3. Market Time & Scheduling

- How do average days between concerts differ between high and low Last.fm listener count artists?
- To what extent does an artist's Last.fm playcount influence the percentage of concerts scheduled on weekends?
- How does lead time (days between sale start and the first concert date) correlate with an artist's Last.fm listener count?

---

# Data Sources

The project integrates the following APIs:

- Last.fm API → Artist, listeners, playcount, tags (genre)
- Ticketmaster API → Event metadata, ticket onsale/offsale, leadtime, weekday/weekend
- Spotify charts → Weekly charts
- Capital cities → capital city/non-capital city

---

# Project Structure

DataScience-Project/
│
├── data/
│   ├── plots/
│   │   ├── correlation_plot.png
│   │   ├── f1_correlation.png
│   │   ├── f1_timeline.png
│   │   └── rq3_liteners_chart_vs_nonchart_boxplot.png
│   │
│   ├── processed/
│   │   ├── spotify_charts/
│   │   │   ├── chart_artists.csv
│   │   │   ├── spotify_artists_streams_monthly.json
│   │   │   ├── spotify_viral_hits.json
│   │   │   ├── spotify_weekly_with_viral_flag.csv
│   │   │   └── spotify_weekly_with_viral_flag.json
│   │   │
│   │   ├── ticketmaster/
│   │   │   └── 2026-03-04.json
│   │   │   
│   │   ├── f2_results.csv
│   │   ├── f3_results.csv
│   │   │── final_dataset.csv
│   │   └── geo_alignment.csv
│   │
│   └── raw/
│       ├── audioscrobbler/
│       │   └── artists_list.csv
│       │
│       │── spotify_charts/
│       │   └── regional-global-weekly # 2023-2026
│       │
│       │── artists_lastfm.csv
│       │── artists_list.csv
│       │── capitals.json
│       │── final_dataset.csv
│       │── last_fm
│       │── lastfm_geo_presence.csv
│       │── lastfm_toptracks.csv
│       │── rq3_lastfm_with_chart_flag.csv
│       │── rq3_listeners_chart_vs_nonchart_summary.csv
│       └── ticketmaster_events.csv
│   
├── src/
│   ├── old/
│   │   ├── analyse_f3_correlation.py
│   │   ├── filter_and_analyse.py
│   │   ├── process_spotify_charts.py
│   │   └── process_spotify_viral.py
│   │
│   ├── research_question_analyses/
│   │   ├── analyse_f1_correlation.py
│   │   ├── analyse_f2_concentration_events.py
│   │   └── analyse_f3.py
│   │
│   └── scripts/
│       ├── data/
│       │   └── raw/
│       │       └── capitals.json
│       │
│       ├── artists.py
│       ├── collect_artists_lastfm.py
│       ├── collect_lastfm_geo.py
│       ├── collect_ticketmaster.py
│       ├── collect_ticketmaster_ORIG.py
│       ├── collect_toptracks.py
│       ├── compute_concentration.py
│       ├── get_artists_list.py
│       ├── get_capitals.py
│       ├── join_data.py
│       └── process_spotify_charts.py
│
├── .env
├── .gitignore
└── README.md

---

# Keys

LASTFM_KEY
TICKETMASTER_KEY

---

# Authors

Selen Erbas,
Ajna Annageldyeva,
Irem Karadeniz,
Ali-Jawad Yusufi
