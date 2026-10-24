"""Place name -> coordinates and elevation (Open-Meteo Geocoding API, data from GeoNames).

Pure Python (no Streamlit). Caching is done in the page that calls it.
"""
import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def finde_ort(name):
    """Ortsname -> Liste möglicher Treffer (Open-Meteo Geocoding, inkl. Höhe)."""
    r = requests.get(
        GEOCODING_URL,
        params={"name": name, "count": 5, "language": "en", "format": "json"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get("results", [])


def ort_label(o):
    """Anzeigename eines Treffers: 'Madison, Wisconsin, United States'."""
    teile = [o.get("name", "?"), o.get("admin1"), o.get("country")]
    return ", ".join(t for t in teile if t)
