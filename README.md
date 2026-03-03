# Live Music: Digital Popularity vs Reality

## From Streams to Stages  
To what extent do digital Spotify metrics predict the physical reality of global concert tours?

---

## Project Objective

This project examines whether digital streaming indicators — particularly Spotify popularity metrics — can predict measurable real-world outcomes in live music performance.

We aim to bridge the gap between:

- **Digital popularity (streams, followers, popularity scores)**
- **Physical concert performance (ticket availability, scheduling, geographic reach)**

The project integrates multiple APIs to construct a structured, reproducible data pipeline for cross-platform analysis.

---

# Research Dimensions

## 1. Streaming & Ticket Power

- How does the number of Spotify followers correlate with the average ticket sales of a current tour for the same artists?
- How does Spotify's "Popularity" metric differ between artists whose events are marked as *off-sale* versus still *on-sale*?
- To what extent does a “Viral Hit” (high Spotify popularity and recent release) correlate with price dynamics (min/max price ranges) and ticket availability on the primary market compared to established artists?

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

- How does the number of Spotify followers correlate with the average ticket sales of a current tour for the same artists?
- How does Spotify's "Popularity" metric differ between artists whose events are marked as "off-sale" versus still "on-sale"?
- To what extent does a “Viral Hit” (high Spotify popularity and recent release) correlate with price dynamics (min/max price ranges) and ticket availability on the primary market compared to established artists?


  2. Geographic Analysis

- What is the ratio of revisit cities to new cities on an artist’s current tour?
- How does ticket availability change depending on the density of similar artists (same genre) performing within a 300km radius in the same time window?
- What proportion of an artist’s performances take place in capital cities compared to non-capital cities?


  3. Market Time & Scheduling

- How does the average number of days between concert dates differ between high and low popularity artists?
- To what extent does an artist’s Spotify popularity score influence the percentage of concerts scheduled on weekends?
- How does lead time (days between sale start and event date) correlate with an artist’s follower count?

---

# Data Sources

The project integrates the following APIs:

- Spotify API → Artist popularity, followers, genre classification
- Ticketmaster API → Event metadata, ticket availability, pricing ranges
- Overpass API (OpenStreetMap) → Venue infrastructure and geographic context
- OpenRouteService API → Distance calculations and routing between locations

---

# Project Structure

DataScience-Project/
│
├── src/
│   ├── fetch_.py
│   ├── process_.py
│
├── data/
│   ├── raw/
│   │   ├── ticketmaster/
│   │   ├── spotify/
│   │   ├── overpass/
│   │   └── openrouteservice/
│   │
│   └── processed/
│
├── .env
├── .gitignore
└── README.md

---

# Keys

TICKETMASTER_KEY
SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET
OPENROUTESERVICE_KEY

---

# Authors

Selen Erbas
Ajna Annageldyeva
Irem Karadeniz
Ali-Jawad Yusufi
