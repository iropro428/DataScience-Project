# =============================================================================
# AI was used both to support development
# and for debugging purposes.
# =============================================================================

import os
import time
import requests
import pandas as pd
import json
from dotenv import load_dotenv
from pathlib import Path
from artists import ARTISTS  

# Load environment variables
load_dotenv()

TM_KEY = os.getenv("TICKETMASTER_API_KEY")
BASE_URL = "https://app.ticketmaster.com/discovery/v2"

# List of keywords for events that are not actual concerts (e.g., VIP packages)
SKIP_KEYWORDS = [
    "vip package", "business seat", "hospitality", "meet & greet", "meet and greet", 
    "premium package", "vip experience", "fan package"]

# Load the list of capital cities
try:
    with open("data/raw/capitals.json") as f:
        CAPITAL_CITIES = set(json.load(f))
    print(f"{len(CAPITAL_CITIES)} capital cities loaded")
except FileNotFoundError:
    print("data/capitals.json not found — please run get_capitals.py first")
    CAPITAL_CITIES = set()

# Function to get the Ticketmaster artist ID
def get_tm_artist_id(artist_name):
    try:
        response = requests.get(f"{BASE_URL}/attractions.json", params={
            "apikey": TM_KEY,
            "keyword": artist_name,
            "size": 1
        })
        print(f"API Response for {artist_name}: {response.status_code}")
        print(response.json())  # Output the JSON response
        data = response.json()
        items = data.get("_embedded", {}).get("attractions", [])
        if not items:
            return None, None
        return items[0]["id"], items[0]["name"]
    except Exception as e:
        print(f"Artist ID error: {e}")
        return None, None

# Function to get events for an artist
def get_events(artist_id, artist_name):
    events = []
    page = 0

    while True:
        try:
            # API call for the artist's events
            response = requests.get(f"{BASE_URL}/events.json", params={
                "apikey": TM_KEY,
                "attractionId": artist_id,
                "size": 200,
                "page": page,
                "sort": "date,asc"
            })

            # Check the status of the API response
            if response.status_code != 200:
                print(f"Error fetching data for {artist_name}: HTTP {response.status_code}")
                break

            data = response.json()

            # Check for errors in the response
            if "error" in data:
                print(f"Error with {artist_name}: {data['error']} - {data.get('message', '')}")
                break

            # If events are present, add them to the list
            items = data.get("_embedded", {}).get("events", [])
            if not items:
                break

            print(f"Fetched {len(items)} events for {artist_name}")  # Debugging print

            for event in items:
                # Extract relevant event information
                venues = event.get("_embedded", {}).get("venues", [{}])
                venue = venues[0] if venues else {}
                city = venue.get("city", {}).get("name", None)
                country = venue.get("country", {}).get("name", None)
                venue_name = venue.get("name", None)

                # Check if it is a capital city
                is_capital = city in CAPITAL_CITIES if city else False

                # Extract event data
                dates = event.get("dates", {})
                start = dates.get("start", {})
                event_date = start.get("localDate", None)

                weekday = None
                is_weekend = None
                if event_date:
                    dt = pd.to_datetime(event_date)
                    weekday = dt.strftime("%A")  # "Monday", "Friday" etc.
                    is_weekend = int(dt.dayofweek) >= 5  # Saturday=5, Sunday=6

                # Extract sales data (Onsale / Offsale Dates)
                sales = event.get("sales", {})
                public = sales.get("public", {})
                onsale_date = public.get("startDateTime", None)
                offsale_date = public.get("endDateTime", None)
                status = dates.get("status", {}).get("code", None)

                # Lead-Time (days between Onsale and Event)
                lead_time_days = None
                if onsale_date and event_date:
                    try:
                        lead_time_days = (
                                pd.to_datetime(event_date) -
                                pd.to_datetime(onsale_date).normalize()
                        ).days
                    except:
                        pass

                # Add the event to the list
                event_data = {
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
                }

                events.append(event_data)

            # If all pages are processed, stop the loop
            total_pages = data.get("page", {}).get("totalPages", 1)
            page += 1
            if page >= total_pages:
                break

            # Avoid rate-limiting by adding a short delay
            time.sleep(0.2)

        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    return events


# Main process
all_events = []

for i, name in enumerate(ARTISTS):
    print(f"\n[{i + 1}/{len(ARTISTS)}] {name}")
    artist_id, tm_name = get_tm_artist_id(name)
    if not artist_id:
        print(f"Not found on Ticketmaster")
        continue
    print(f"TM Artist: {tm_name} (ID: {artist_id})")
    events = get_events(artist_id, name)
    all_events.extend(events)
    time.sleep(0.4)

# Save the data to a CSV file
os.makedirs("data/raw", exist_ok=True)
df = pd.DataFrame(all_events)
df.to_csv("data/raw/ticketmaster_events.csv", index=False)

total = len(df)

print(f"\n{total} events saved → data/raw/ticketmaster_events.csv")
