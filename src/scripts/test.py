import requests, json

API_KEY = "5d2b509c1cae614e98ab74dc1972236d"

params = {
    "method": "geo.gettopartists",
    "country": "Germany",
    "api_key": API_KEY,
    "format": "json",
    "limit": 5
}

r = requests.get("https://ws.audioscrobbler.com/2.0/", params=params, timeout=20)
data = r.json()

artists = data.get("topartists", {}).get("artist", [])
print(json.dumps(artists[0], indent=2))