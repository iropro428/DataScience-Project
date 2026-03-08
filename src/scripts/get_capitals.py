# get_capitals.py
# Lädt alle Hauptstädte via RestCountries API und speichert sie in data/raw/capitals.json
import requests, json, os


def get_capital_cities():
    response = requests.get("https://restcountries.com/v3.1/all?fields=capital")
    data = response.json()

    capitals = set()
    for country in data:
        for capital in country.get("capital", []):
            if capital:
                capitals.add(capital)

    print(f"✅ {len(capitals)} Hauptstädte geladen")
    return capitals


if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    CAPITAL_CITIES = get_capital_cities()
    out = "data/raw/capitals.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(sorted(CAPITAL_CITIES), f, ensure_ascii=False, indent=2)
    print(f"✅ Gespeichert → {out}")
