# get_capitals.py
import requests


def get_capital_cities():
    response = requests.get("https://restcountries.com/v3.1/all?fields=capital")
    data = response.json()

    capitals = set()
    for country in data:
        for capital in country.get("capital", []):
            if capital:
                capitals.add(capital)

    print(f" {len(capitals)} Hauptstädte geladen")
    return capitals


CAPITAL_CITIES = get_capital_cities()
