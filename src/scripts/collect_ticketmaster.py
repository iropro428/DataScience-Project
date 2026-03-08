# collect_ticketmaster.py  —  v2  (mit Ticket-Preisen für F2)
import requests, pandas as pd, time, os, json
from dotenv import load_dotenv
from pathlib import Path

# .env suchen: erst neben dem Script, dann im Projektroot (2 Ebenen hoch)
_script_dir = Path(__file__).resolve().parent
for _candidate in [
    _script_dir / ".env",
    _script_dir.parent / ".env",
    _script_dir.parent.parent / ".env",
]:
    if _candidate.exists():
        load_dotenv(_candidate)
        print(f"✅ .env geladen: {_candidate}")
        break
else:
    load_dotenv()  # Fallback: CWD

TM_KEY = os.getenv("TICKETMASTER_API_KEY")
if not TM_KEY:
    print("❌ TICKETMASTER_API_KEY nicht gefunden!")
    print("   Stelle sicher dass .env die Zeile enthält:")
    print("   TICKETMASTER_API_KEY=dein_key_hier")
    import sys;

    sys.exit(1)
print(f"✅ API Key geladen ({TM_KEY[:8]}...)")
BASE_URL = "https://app.ticketmaster.com/discovery/v2"

# Package-Events die kein eigenes Konzert sind (VIP, Business Seat etc.)
SKIP_KEYWORDS = [
    "vip package", "business seat", "hospitality", "meet & greet", "meet and greet", "premium package", "vip experience", "fan package"]

# ── Artist-Liste laden ────────────────────────────────────────────────────
try:
    from artists import ARTISTS
except ImportError:
    df_list = pd.read_csv("data/artists_list.csv")
    ARTISTS = df_list["name"].tolist()

# ── Hauptstädte laden ─────────────────────────────────────────────────────
try:
    with open("data/raw/capitals.json") as f:
        CAPITAL_CITIES = set(json.load(f))
    print(f"✅ {len(CAPITAL_CITIES)} Hauptstädte geladen")
except FileNotFoundError:
    print("⚠️  data/capitals.json nicht gefunden — bitte get_capitals.py ausführen")
    CAPITAL_CITIES = set()


# ── Artist ID holen ───────────────────────────────────────────────────────
def get_tm_artist_id(artist_name):
    try:
        r = requests.get(f"{BASE_URL}/attractions.json", params={
            "apikey": TM_KEY,
            "keyword": artist_name,
            "size": 1
        }, timeout=10)
        items = r.json().get("_embedded", {}).get("attractions", [])
        if not items:
            return None, None
        return items[0]["id"], items[0]["name"]
    except Exception as e:
        print(f"  ⚠️  Artist-ID Fehler: {e}")
        return None, None


# ── Events für Artist holen ───────────────────────────────────────────────
def get_events(artist_id, artist_name):
    events = []
    page = 0

    while True:
        try:
            r = requests.get(f"{BASE_URL}/events.json", params={
                "apikey": TM_KEY,
                "attractionId": artist_id,
                "size": 200,
                "page": page,
                "sort": "date,asc"
            }, timeout=15)
            data = r.json()
            items = data.get("_embedded", {}).get("events", [])
            if not items:
                break

            for event in items:

                # ── Package-Events überspringen (VIP, Business Seat, etc.) ──
                event_name_raw = (event.get("name") or "").lower()
                if any(kw in event_name_raw for kw in SKIP_KEYWORDS):
                    continue

                # ── Venue ─────────────────────────────────────────────────
                venues = event.get("_embedded", {}).get("venues", [{}])
                venue = venues[0] if venues else {}
                city = venue.get("city", {}).get("name", None)
                country = venue.get("country", {}).get("name", None)
                venue_name = venue.get("name", None)
                is_capital = city in CAPITAL_CITIES if city else False

                # ── Datum ─────────────────────────────────────────────────
                dates = event.get("dates", {})
                start = dates.get("start", {})
                event_date = start.get("localDate", None)
                weekday = None
                is_weekend = None
                if event_date:
                    try:
                        dt = pd.to_datetime(event_date)
                        weekday = dt.strftime("%A")  # "Monday", "Friday" etc.
                        is_weekend = int(dt.dayofweek) >= 5  # dayofweek = Property (0=Mo, 6=So)
                    except Exception:
                        weekday = None
                        is_weekend = None

                # ── Sales (Onsale / Offsale Datum) ────────────────────────
                sales = event.get("sales", {})
                public = sales.get("public", {})
                onsale_date = public.get("startDateTime", None)
                offsale_date = public.get("endDateTime", None)
                tm_status = dates.get("status", {}).get("code", None)

                # ── Lead Time ─────────────────────────────────────────────
                lead_time_days = None
                if onsale_date and event_date:
                    try:
                        lead_time_days = (
                                pd.to_datetime(event_date) -
                                pd.to_datetime(onsale_date).normalize()
                        ).days
                    except:
                        pass

                # ── Presale Info ──────────────────────────────────────────
                presales = sales.get("presales", [])
                has_presale = len(presales) > 0
                n_presales = len(presales)

                # ── Ticket Preise  (NEU für F2) ───────────────────────────
                price_ranges = event.get("priceRanges", [])
                ticket_price_min = None
                ticket_price_max = None
                ticket_price_avg = None
                ticket_currency = None

                if price_ranges:
                    pr = price_ranges[0]  # erster Preisbereich
                    ticket_price_min = pr.get("min", None)
                    ticket_price_max = pr.get("max", None)
                    ticket_currency = pr.get("currency", None)
                    if ticket_price_min is not None and ticket_price_max is not None:
                        ticket_price_avg = round(
                            (ticket_price_min + ticket_price_max) / 2, 2
                        )

                events.append({
                    "artist_name": artist_name,
                    "event_id": event.get("id"),
                    "event_name": event.get("name"),
                    "event_date": event_date,
                    "weekday": weekday,
                    "is_weekend": is_weekend,
                    "tm_status": tm_status,  # onsale/offsale/cancelled
                    "onsale_date": onsale_date,
                    "offsale_date": offsale_date,
                    "lead_time_days": lead_time_days,
                    "has_presale": has_presale,
                    "n_presales": n_presales,
                    "ticket_price_min": ticket_price_min,
                    "ticket_price_max": ticket_price_max,
                    "ticket_price_avg": ticket_price_avg,
                    "ticket_currency": ticket_currency,
                    "venue_name": venue_name,
                    "city": city,
                    "country": country,
                    "is_capital": is_capital,
                    "latitude": venue.get("location", {}).get("latitude"),
                    "longitude": venue.get("location", {}).get("longitude"),
                })

            total_pages = data.get("page", {}).get("totalPages", 1)
            page += 1
            if page >= total_pages:
                break
            time.sleep(0.2)

        except Exception as e:
            print(f"  ⚠️  Events Fehler Seite {page}: {e}")
            break

    return events


# ── Main ──────────────────────────────────────────────────────────────────
all_events = []

for i, name in enumerate(ARTISTS):
    print(f"\n[{i + 1}/{len(ARTISTS)}] {name}")
    artist_id, tm_name = get_tm_artist_id(name)
    if not artist_id:
        print(f"  ❌ Nicht gefunden auf Ticketmaster")
        continue
    print(f"  🎤 TM: {tm_name} (ID: {artist_id})")
    events = get_events(artist_id, name)
    n_with_price = sum(1 for e in events if e["ticket_price_avg"] is not None)
    print(f"  ✅ {len(events)} Events  |  {n_with_price} mit Ticketpreis")
    all_events.extend(events)
    time.sleep(0.4)

# ── Speichern ─────────────────────────────────────────────────────────────
os.makedirs("data/raw", exist_ok=True)
df = pd.DataFrame(all_events)
df.to_csv("data/raw/ticketmaster_events.csv", index=False)

total = len(df)
w_price = df["ticket_price_avg"].notna().sum()
pct_price = w_price / total * 100 if total > 0 else 0

print(f"\n✅ {total} Events gespeichert → data/raw/ticketmaster_events.csv")
print(f"   davon mit Ticketpreis: {w_price} ({pct_price:.1f}%)")
print(f"\nPreis-Statistik:")
print(df["ticket_price_avg"].describe().round(2))
