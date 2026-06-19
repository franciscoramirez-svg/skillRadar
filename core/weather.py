import os

import requests


API_KEY_ENV = "OPENWEATHER_API_KEY"
URL_BASE = "https://api.openweathermap.org/data/2.5/weather"


def obtener_clima(ciudad: str = "Veracruz", pais: str = "MX") -> dict | None:
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        return None

    params = {
        "q": f"{ciudad},{pais}",
        "appid": api_key,
        "units": "metric",
        "lang": "es",
    }

    try:
        resp = requests.get(URL_BASE, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "city": data["name"],
        }
    except requests.RequestException:
        return None
