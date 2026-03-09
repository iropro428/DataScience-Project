# get_capitals.py
# Loads all capital cities via the RestCountries API and saves them to data/raw/capitals.json
import requests, json, os


def get_capital_cities():
    response = requests.get("https://restcountries.com/v3.1/all?fields=capital")
    data = response.json()

    capitals = set()
    for country in data:
        for capital in country.get("capital", []):
            if capital:
                capitals.add(capital)

<<<<<<< HEAD
    print(f" {len(capitals)} Hauptstädte geladen")
=======
    print(f" {len(capitals)} load capital cities")
>>>>>>> 73d1ee7cfef4d45a9bd08f49ba629403e7265cc0
    return capitals


if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    CAPITAL_CITIES = get_capital_cities()
    out = "data/raw/capitals.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(sorted(CAPITAL_CITIES), f, ensure_ascii=False, indent=2)
<<<<<<< HEAD
    print(f" Gespeichert → {out}")
=======
    print(f" saved → {out}")
>>>>>>> 73d1ee7cfef4d45a9bd08f49ba629403e7265cc0
