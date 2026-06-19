import os

import requests


API_KEY_ENV = "OPENWEATHER_API_KEY"
URL_BASE = "https://api.openweathermap.org/data/2.5/weather"


def obtener_clima(ciudad: str = "Veracruz", pais: str = "MX") -> dict:
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        return {"error": "No hay API Key configurada", "ok": False}

    params = {
        "q": f"{ciudad},{pais}",
        "appid": api_key,
        "units": "metric",
        "lang": "es",
    }

    try:
        resp = requests.get(URL_BASE, params=params, timeout=15)
        if resp.status_code == 401:
            return {"error": "API Key inválida", "ok": False}
        if resp.status_code == 404:
            return {"error": f"Ciudad '{ciudad}' no encontrada", "ok": False}
        resp.raise_for_status()
        data = resp.json()
        return {
            "ok": True,
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "city": data["name"],
        }
    except requests.Timeout:
        return {"error": "Tiempo de espera agotado", "ok": False}
    except requests.RequestException as e:
        return {"error": f"Error de conexión: {str(e)[:60]}", "ok": False}
