import json
import os
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv


ARTISTS = ["Bad Bunny", "The Weeknd", "Bruno Mars"]


def get_spotify_token(client_id: str, client_secret: str) -> str:
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def get_spotify_artist_popularity(artist_name: str, token: str) -> dict:
    # 1) Search -> get artist id (simplified object)
    s = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": artist_name, "type": "artist", "limit": 1},
        timeout=30,
    )
    s.raise_for_status()
    items = s.json().get("artists", {}).get("items", [])
    if not items:
        return {"found": False, "name": artist_name, "popularity": None, "followers": None, "spotify_id": None}

    artist_id = items[0].get("id")
    if not artist_id:
        return {"found": False, "name": artist_name, "popularity": None, "followers": None, "spotify_id": None}

    # 2) Get full artist object (includes popularity + followers)
    a = requests.get(
        f"https://api.spotify.com/v1/artists/{artist_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    a.raise_for_status()
    data = a.json()

    return {
        "found": True,
        "name": data.get("name"),
        "spotify_id": data.get("id"),
        "popularity": data.get("popularity"),
        "followers": (data.get("followers") or {}).get("total"),
    }

def fetch_ticketmaster_events_for_artist(artist_name: str, api_key: str, size: int = 100) -> list[dict]:
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": api_key,
        "keyword": artist_name,
        "size": size,
        "sort": "date,asc",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    events = data.get("_embedded", {}).get("events", [])
    # extract minimal fields + status
    cleaned = []
    for e in events:
        status = e.get("dates", {}).get("status", {}).get("code")
        name = e.get("name")
        url = e.get("url")
        dt = e.get("dates", {}).get("start", {}).get("dateTime")
        local_date = e.get("dates", {}).get("start", {}).get("localDate")
        cleaned.append(
            {
                "event_id": e.get("id"),
                "event_name": name,
                "status": status,
                "dateTime_utc": dt,
                "local_date": local_date,
                "url": url,
            }
        )
    return cleaned


def main():
    load_dotenv()
    tm_key = os.getenv("TICKETMASTER_KEY")
    sp_id = os.getenv("SPOTIFY_CLIENT_ID")
    sp_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not tm_key:
        raise RuntimeError("TICKETMASTER_KEY fehlt in .env")
    if not sp_id or not sp_secret:
        raise RuntimeError("SPOTIFY_CLIENT_ID/SECRET fehlen in .env")

    token = get_spotify_token(sp_id, sp_secret)

    results = []
    for artist in ARTISTS:
        sp = get_spotify_artist_popularity(artist, token)
        tm_events = fetch_ticketmaster_events_for_artist(artist, tm_key)

        onsale = sum(1 for e in tm_events if e.get("status") == "onsale")
        offsale = sum(1 for e in tm_events if e.get("status") == "offsale")

        results.append(
            {
                "artist_query": artist,
                "spotify": sp,
                "ticketmaster": {
                    "n_events_found": len(tm_events),
                    "onsale": onsale,
                    "offsale": offsale,
                    "events_sample": tm_events[:10],  # nur ein sample, damit JSON nicht riesig wird
                },
            }
        )

    out = {
        "created_at": date.today().isoformat(),
        "research_question": "How does Spotify popularity differ between artists whose events are still onsale and those whose events are already offsale?",
        "artists": results,
        "note": "Ticketmaster 'offsale' can mean sold out OR sales ended OR not currently on sale (depends on event).",
    }

    out_dir = Path("data/processed/rq")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"rq_spotify_popularity_onsale_offsale_{date.today().isoformat()}.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Saved:", out_path)


if __name__ == "__main__":
    main()
