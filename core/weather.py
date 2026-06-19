import os

import requests


API_KEY_ENV = "WEATHERAPI_KEY"
URL_BASE = "https://api.weatherapi.com/v1/current.json"


def obtener_clima(ciudad: str = "Veracruz", pais: str = "") -> dict:
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        return {"error": "No hay API Key configurada", "ok": False}

    q = f"{ciudad},{pais}" if pais else ciudad

    params = {"key": api_key, "q": q, "lang": "es"}

    try:
        resp = requests.get(URL_BASE, params=params, timeout=15)
        if resp.status_code == 401:
            return {"error": "API Key inválida", "ok": False}
        if resp.status_code == 400:
            return {"error": f"Ciudad '{ciudad}' no encontrada", "ok": False}
        resp.raise_for_status()
        data = resp.json()
        current = data["current"]
        return {
            "ok": True,
            "temp": current["temp_c"],
            "humidity": current["humidity"],
            "description": current["condition"]["text"],
            "city": data["location"]["name"],
        }
    except requests.Timeout:
        return {"error": "Tiempo de espera agotado", "ok": False}
    except requests.RequestException as e:
        return {"error": f"Error de conexión: {str(e)[:60]}", "ok": False}
