# collect_ticketmaster_ORIG.py
import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

from get_capitals import get_capital_cities

load_dotenv()

TM_KEY = os.getenv("TICKETMASTER_API_KEY")
BASE_URL = "https://app.ticketmaster.com/discovery/v2"

# Artist-List
from alt.artists import ARTISTS


# 1. get Artist ID from Ticketmaster
def get_tm_artist_id(artist_name):
    try:
        response = requests.get(f"{BASE_URL}/attractions.json", params={
            "apikey": TM_KEY,
            "keyword": artist_name,
            "size": 1
        })
        data = response.json()
        items = data.get("_embedded", {}).get("attractions", [])
        if not items:
            return None, None
        return items[0]["id"], items[0]["name"]
    except Exception as e:
        print(f" Artist-ID Fehler: {e}")
        return None, None


# 2. get Events from Artist 
def get_events(artist_id, artist_name):
    events = []
    page = 0

    while True:
        try:
            response = requests.get(f"{BASE_URL}/events.json", params={
                "apikey": TM_KEY,
                "attractionId": artist_id,
                "size": 200,
                "page": page,
                "sort": "date,asc"
            })

            data = response.json()

            items = data.get("_embedded", {}).get("events", [])
            if not items:
                break

            for event in items:
                # Venue Informations
                venues = event.get("_embedded", {}).get("venues", [{}])
                venue = venues[0] if venues else {}
                city = venue.get("city", {}).get("name", None)
                country = venue.get("country", {}).get("name", None)
                venue_name = venue.get("name", None)

                # Capital city?
                is_capital = venue.get("city", {}).get("name") in CAPITAL_CITIES

                # Date
                dates = event.get("dates", {})
                start = dates.get("start", {})
                event_date = start.get("localDate", None)

                # Weekday
                weekday = None
                is_weekend = None
                if event_date:
                    dt = pd.to_datetime(event_date)
                    weekday = dt.day_name()
                    is_weekend = dt.weekday() >= 5  # Sa=5, So=6

                # Onsale / Offsale
                sales = event.get("sales", {})
                public = sales.get("public", {})
                onsale_date = public.get("startDateTime", None)
                offsale_date = public.get("endDateTime", None)
                status = dates.get("status", {}).get("code", None)

                # Lead time (Days between Onsale and Event)
                lead_time_days = None
                if onsale_date and event_date:
                    try:
                        lead_time_days = (
                                pd.to_datetime(event_date) -
                                pd.to_datetime(onsale_date).normalize()
                        ).days
                    except:
                        pass

                events.append({
                    "artist_name": artist_name,
                    "event_id": event.get("id"),
                    "event_name": event.get("name"),
                    "event_date": event_date,
                    "weekday": weekday,
                    "is_weekend": is_weekend,
                    "status": status,  
                    "onsale_date": onsale_date,
                    "offsale_date": offsale_date,
                    "lead_time_days": lead_time_days,
                    "venue_name": venue_name,
                    "city": city,
                    "country": country,
                    "is_capital": is_capital,
                    "latitude": venue.get("location", {}).get("latitude"),
                    "longitude": venue.get("location", {}).get("longitude"),
                })

            # next page?
            total_pages = data.get("page", {}).get("totalPages", 1)
            page += 1
            if page >= total_pages:
                break

            time.sleep(0.2)

        except Exception as e:
            print(f" Events Fehler Seite {page}: {e}")
            break

    return events


if __name__ == '__main__':
    # List of capitals 
    CAPITAL_CITIES = get_capital_cities()

    # main
    all_events = []

    for i, name in enumerate(ARTISTS):
        print(f"\n[{i + 1}/{len(ARTISTS)}] {name}")

        artist_id, tm_name = get_tm_artist_id(name)
        if not artist_id:
            print(f"  Nicht gefunden auf Ticketmaster")
            continue

        print(f"  TM Artist: {tm_name} (ID: {artist_id})")

        events = get_events(artist_id, name)
        print(f"   {len(events)} Events gefunden")
        all_events.extend(events)

        time.sleep(0.5)

    # Save CSV
    df_events = pd.DataFrame(all_events)
    os.makedirs("data", exist_ok=True)
    df_events.to_csv("data/raw/ticketmaster/ticketmaster_events.csv", index=False)
    print(f"\n {len(df_events)} Events total → data/ticketmaster_events.csv")
