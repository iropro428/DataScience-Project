# get_artists_list.py
import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "https://ws.audioscrobbler.com/2.0/"


def get_top_artists(pages=5):  # 1 page = 50 artists → 5 pages = 250 artists
    all_artists = []

    for page in range(1, pages + 1):
        print(f"Lade Seite {page}/{pages}...")

        response = requests.get(BASE_URL, params={
            "method": "chart.gettopartists",
            "api_key": API_KEY,
            "format": "json",
            "limit": 50,
            "page": page
        })

        data = response.json()
        artists = data["artists"]["artist"]

        for a in artists:
            all_artists.append(a["name"])

        time.sleep(0.3)

    return all_artists


# ── Ausführen ─────────────────────────────────────────
artists = get_top_artists(pages=10)  # = 500 Artists

print(f"✅ {len(artists)} Artists gesammelt")

# Als Python-Liste speichern
with open("alt/artists.py", "w") as f:
    f.write("ARTISTS = [\n")
    for a in artists:
        # Anführungszeichen im Namen escapen
        a_clean = a.replace('"', '\\"')
        f.write(f'    "{a_clean}",\n')
    f.write("]\n")

print("✅ artists.py gespeichert")

# Als CSV speichern
pd.DataFrame({"name": artists}).to_csv("data/artists_list.csv", index=False)
print("✅ data/audioscrobbler/artists_list.csv gespeichert")
