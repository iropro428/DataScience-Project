# join_data.py
# Aggregiert Rohdaten → data/processed/final_dataset.csv
# Forschungsfragen: F2, F4, F6, F7 + Basis für alle anderen
#
# Input:
#   data/raw/artists_lastfm.csv
#   data/raw/ticketmaster_events.csv
#   data/raw/lastfm_toptracks.csv          (optional, F2)
#
# Output:
#   data/processed/final_dataset.csv
#   data/processed/f4_city_frequencies.csv
#   data/processed/f6_capitals_visited.csv
#   data/processed/f6_capitals_per_artist.csv

import pandas as pd
import numpy as np
from datetime import date
import os, sys

os.makedirs("data/processed", exist_ok=True)

# ── Rohdaten laden ─────────────────────────────────────────────────────────
for p in ["data/raw/artists_lastfm.csv", "data/raw/ticketmaster_events.csv"]:
    if not os.path.exists(p):
        print(f"❌  {p} fehlt");
        sys.exit(1)

df_lastfm = pd.read_csv("data/raw/artists_lastfm.csv")
df_events = pd.read_csv("data/raw/ticketmaster_events.csv")
print(f"Last.fm Artists:     {len(df_lastfm)}")
print(f"Ticketmaster Events: {len(df_events)}")

today = pd.Timestamp(date.today())
one_year_ago = today - pd.DateOffset(years=1)

df_events["event_date_dt"] = pd.to_datetime(df_events["event_date"], errors="coerce")
df_events["onsale_date_dt"] = pd.to_datetime(df_events["onsale_date"], errors="coerce", utc=True).dt.tz_localize(None)
df_events["is_weekend"] = pd.to_numeric(df_events["is_weekend"], errors="coerce")
df_events["is_capital"] = pd.to_numeric(df_events["is_capital"], errors="coerce")

# ── Lead Time: Nur zukünftige Events — 1 Wert pro Artist ─────────────────
# Nur Artists die mindestens ein zukünftiges Event haben.
# Pro Artist:
#   first_event_date  = frühestes event_date >= today
#   first_onsale_date = frühestes onsale_date dieser zukünftigen Events
#   lead_time_days    = first_event_date - first_onsale_date
_df_future = df_events[
    (df_events["event_date_dt"] >= today) &
    df_events["onsale_date_dt"].notna()
    ].copy()

_first_event = _df_future.groupby("artist_name")["event_date_dt"].min().rename("first_event_date")
_first_onsale = _df_future.groupby("artist_name")["onsale_date_dt"].min().rename("first_onsale_date")
_lead_df = pd.concat([_first_event, _first_onsale], axis=1).dropna()
_lead_df["lead_time_days"] = (_lead_df["first_event_date"] - _lead_df["first_onsale_date"]).dt.days
_lead_df.loc[_lead_df["lead_time_days"] < 0, "lead_time_days"] = None  # Datenfehler
n_lead = _lead_df["lead_time_days"].notna().sum()
print(f"lead_time_days: {n_lead} Artists mit zukuenftigem Event + onsale_date "
      f"(Median: {_lead_df['lead_time_days'].median():.0f} Tage)")

# ── Dedup: VIP/Package-Events entfernen ───────────────────────────────────
# Ticketmaster listet VIP Packages, Business Seats etc. als eigene Events
# → kein eigenes Konzert, verfälscht Event-Zählungen
SKIP_KW = ["vip package", "business seat", "hospitality",
           "meet & greet", "meet and greet", "premium package",
           "vip experience", "fan package"]

n_before = len(df_events)
if "event_name" in df_events.columns:
    mask_pkg = df_events["event_name"].str.lower().str.contains(
        "|".join(SKIP_KW), na=False
    )
    df_events = df_events[~mask_pkg].copy()
    n_removed = n_before - len(df_events)
    print(f"🔧 Dedup Packages: {n_removed} Package-Events entfernt ({n_before} → {len(df_events)})")

# Zusatz-Dedup: selber Artist + selbe Stadt + selbes Datum → nur 1 Event behalten
# (fängt sonstige Duplikate wie "Einfache" vs "Sitzplatz" etc.)
n_before2 = len(df_events)
df_events = df_events.sort_values("event_name").drop_duplicates(
    subset=["artist_name", "city", "event_date"], keep="first"
)
n_removed2 = n_before2 - len(df_events)
if n_removed2 > 0:
    print(f"🔧 Dedup Datum/Stadt: {n_removed2} weitere Duplikate entfernt ({n_before2} → {len(df_events)})")

# ══════════════════════════════════════════════════════════════════════════
# 1) BASIS-AGGREGATION
# ══════════════════════════════════════════════════════════════════════════
tour_base = (
    df_events.groupby("artist_name")
    .agg(
        total_events=("event_id", "count"),
        weekend_events=("is_weekend", "sum"),
        countries=("country", "nunique"),
        cities=("city", "nunique"),
    )
    .reset_index()
)
tour_base["pct_weekend"] = (
        tour_base["weekend_events"] / tour_base["total_events"] * 100
).round(2)


# ══════════════════════════════════════════════════════════════════════════
# 2) TOURING STATUS
# ══════════════════════════════════════════════════════════════════════════
def get_touring_status(group):
    future = int((group["event_date_dt"] >= today).sum())
    pct = future / len(group) if len(group) > 0 else 0
    return pd.Series({
        "touring_status": "active_tour" if pct >= 0.5 else
        "winding_down" if pct > 0 else "tour_completed",
        "future_events": future,
        "pct_future_events": round(pct * 100, 2),
    })


touring_df = df_events.groupby("artist_name").apply(get_touring_status, include_groups=False).reset_index()

# ══════════════════════════════════════════════════════════════════════════
# 3) F2 — Events letztes Jahr (Tour-Intensität)
# ══════════════════════════════════════════════════════════════════════════
events_lastyear = (
    df_events[
        (df_events["event_date_dt"] >= one_year_ago) &
        (df_events["event_date_dt"] <= today)
        ]
    .groupby("artist_name")["event_id"]
    .count()
    .reset_index()
    .rename(columns={"event_id": "events_last_year"})
)


# ══════════════════════════════════════════════════════════════════════════
# 4) F4 — REVISIT vs. NEW CITIES
#
#   new_cities         = Städte mit genau 1 Besuch
#   revisit_cities     = Städte mit ≥ 2 Besuchen
#   pct_revisit_cities = revisit / (revisit + new) × 100       [% Städte]
#   revisit_ratio      = revisit_cities / new_cities
#   pct_events_revisit = Events in Revisit-Städten / total × 100  [% Events]
# ══════════════════════════════════════════════════════════════════════════
def f4_revisit(group):
    counts = group["city"].dropna().value_counts()
    if len(counts) == 0:
        return pd.Series({k: v for k, v in [
            ("revisit_cities", 0), ("new_cities", 0), ("pct_revisit_cities", 0.0),
            ("revisit_ratio", None), ("pct_events_revisit", 0.0),
            ("most_visited_city", None), ("most_visited_n", 0)]})
    revisit = int((counts >= 2).sum())
    new = int((counts == 1).sum())
    total_c = len(counts)
    ev_rev = int(counts[counts >= 2].sum())
    ev_total = int(counts.sum())
    return pd.Series({
        "revisit_cities": revisit,
        "new_cities": new,
        "pct_revisit_cities": round(revisit / total_c * 100, 2) if total_c > 0 else 0.0,
        "revisit_ratio": round(revisit / new, 3) if new > 0 else None,
        "pct_events_revisit": round(ev_rev / ev_total * 100, 2) if ev_total > 0 else 0.0,
        "most_visited_city": str(counts.index[0]),
        "most_visited_n": int(counts.iloc[0]),
    })


revisit_df = df_events.groupby("artist_name").apply(f4_revisit, include_groups=False).reset_index()

# F4 Detail: Artist × Stadt × Besuche
agg_dict = {"visits": ("event_id", "count"), "first_visit": ("event_date", "min"),
            "last_visit": ("event_date", "max"), "is_capital": ("is_capital", "first")}
if "latitude" in df_events.columns:
    agg_dict.update({"latitude": ("latitude", "first"), "longitude": ("longitude", "first")})
city_freq = df_events.groupby(["artist_name", "city", "country"]).agg(**agg_dict).reset_index()
city_freq["is_revisit"] = (city_freq["visits"] >= 2).astype(int)
city_freq.to_csv("data/processed/f4_city_frequencies.csv", index=False)
print(f"✅  f4_city_frequencies.csv     → {len(city_freq)} Einträge")


# ══════════════════════════════════════════════════════════════════════════
# 5) F6 — CAPITAL vs. NON-CAPITAL CITIES
#
#   capital_events      = Events in Hauptstädten (is_capital = 1)
#   non_capital_events  = Events in Nicht-Hauptstädten
#   pct_capital         = capital_events / total_events × 100       [% Events]
#   capital_ratio       = capital_events / non_capital_events
#   unique_capitals     = Anzahl verschiedener Hauptstädte besucht
#   unique_non_capitals = Anzahl verschiedener Nicht-Hauptstädte besucht
#   pct_capital_cities  = unique_capitals / alle_städte × 100       [% Städte]
#
#   Unterschied pct_capital vs pct_capital_cities:
#     pct_capital       → misst Anteil am Konzertvolumen
#     pct_capital_cities → misst Anteil an der geografischen Breite
# ══════════════════════════════════════════════════════════════════════════
def f6_capital(group):
    cap = group["is_capital"].fillna(0)
    total = len(group)
    cap_ev = int(cap.sum())
    non_ev = total - cap_ev

    cap_cities = group[cap == 1]["city"].dropna().nunique()
    non_cap_cities = group[cap == 0]["city"].dropna().nunique()
    total_cities = cap_cities + non_cap_cities

    return pd.Series({
        "capital_events": cap_ev,
        "non_capital_events": non_ev,
        "pct_capital": round(cap_ev / total * 100, 2) if total > 0 else 0.0,
        "capital_ratio": round(cap_ev / non_ev, 3) if non_ev > 0 else None,
        "unique_capitals": cap_cities,
        "unique_non_capitals": non_cap_cities,
        "pct_capital_cities": round(cap_cities / total_cities * 100, 2) if total_cities > 0 else 0.0,
    })


capital_df = df_events.groupby("artist_name").apply(f6_capital, include_groups=False).reset_index()

# F6 Detail 1: Welche Hauptstädte gesamt am häufigsten besucht?
capitals_visited = (
    df_events[df_events["is_capital"] == 1]
    .groupby(["city", "country"])
    .agg(total_visits=("event_id", "count"), n_artists=("artist_name", "nunique"),
         first_seen=("event_date", "min"), last_seen=("event_date", "max"))
    .reset_index()
    .sort_values("total_visits", ascending=False)
)
capitals_visited.to_csv("data/processed/f6_capitals_visited.csv", index=False)
print(f"✅  f6_capitals_visited.csv      → {len(capitals_visited)} Hauptstädte")

# F6 Detail 2: Pro Artist, welche Hauptstädte wie oft?
capitals_per_artist = (
    df_events[df_events["is_capital"] == 1]
    .groupby(["artist_name", "city", "country"])
    .agg(visits=("event_id", "count"), first_visit=("event_date", "min"),
         last_visit=("event_date", "max"))
    .reset_index()
)
capitals_per_artist.to_csv("data/processed/f6_capitals_per_artist.csv", index=False)
print(f"✅  f6_capitals_per_artist.csv   → {len(capitals_per_artist)} Einträge")


# ══════════════════════════════════════════════════════════════════════════
# 6) F7 — Ø Tage zwischen Konzerten
# ══════════════════════════════════════════════════════════════════════════
def avg_days_between(group):
    dates = group["event_date_dt"].dropna().sort_values()
    if len(dates) < 2:
        return None
    return round(dates.diff().dropna().dt.days.mean(), 1)


days_df = df_events.groupby("artist_name").apply(avg_days_between, include_groups=False).reset_index()
days_df.columns = ["artist_name", "avg_days_between_shows"]

# ══════════════════════════════════════════════════════════════════════════
# 7) F2 — STREAMING-KONZENTRATION (optional)
# ══════════════════════════════════════════════════════════════════════════
conc_df = None
if os.path.exists("data/raw/lastfm_toptracks.csv"):
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from compute_concentration import compute_concentration

        conc_df = compute_concentration(pd.read_csv("data/raw/lastfm_toptracks.csv"))
        print(f"✅  Streaming-Konzentration:     {len(conc_df)} Artists")
    except Exception as e:
        print(f"⚠️   compute_concentration: {e}")

# ══════════════════════════════════════════════════════════════════════════
# 8) ZUSAMMENFÜHREN
# ══════════════════════════════════════════════════════════════════════════
df_final = tour_base.copy()
# lead_time_days einmergen (berechnet aus first_onsale_date → first_event_date)
df_final = df_final.merge(
    _lead_df[["lead_time_days"]].reset_index().rename(columns={"artist_name": "artist_name"}),
    on="artist_name", how="left"
)
for sub in [touring_df, events_lastyear, revisit_df, capital_df, days_df]:
    df_final = df_final.merge(sub, on="artist_name", how="left")
if conc_df is not None:
    df_final = df_final.merge(conc_df, on="artist_name", how="left")

lastfm_cols = [c for c in ["name", "listeners", "playcount", "tags"] if c in df_lastfm.columns]
df_final = (
    df_final
    .merge(df_lastfm[lastfm_cols], left_on="artist_name", right_on="name", how="inner")
    .drop(columns=["name"], errors="ignore")
)
df_final = df_final[df_final["total_events"] > 0].copy()
df_final.to_csv("data/processed/final_dataset.csv", index=False)

print(f"\n✅  {len(df_final)} Artists → data/processed/final_dataset.csv")
print(f"    {len(df_final.columns)} Spalten")

# Schnellcheck F4 + F6
for label, cols in [
    ("F4", ["pct_revisit_cities", "revisit_ratio"]),
    ("F6", ["pct_capital", "pct_capital_cities", "unique_capitals"]),
]:
    available = [c for c in cols if c in df_final.columns]
    if available:
        print(f"\n--- {label} ---")
        for c in available:
            val = pd.to_numeric(df_final[c], errors="coerce").mean()
            print(f"  Ø {c:<25} {val:.2f}")
