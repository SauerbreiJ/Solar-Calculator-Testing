"""Reusable Streamlit widget: place name -> coordinates (shared by several pages).

Lives in ui/ (not solar/) because it uses Streamlit; solar/ stays pure Python.
"""
import requests
import streamlit as st

from solar.geocoding import finde_ort, ort_label


@st.cache_data(show_spinner=False)
def suche_ort(name):
    """Gecachte Ortssuche, damit derselbe Name nicht bei jedem Klick neu abgefragt wird."""
    return finde_ort(name)


def location_input(prefix, default="Madison", show_elevation=True):
    """
    Text field + match list for a place name. Must be called OUTSIDE st.form so the
    list of matches appears immediately.

    prefix: unique key prefix per page (widget keys become '<prefix>_ort', ...).
    Returns the selected match (dict with 'latitude', 'elevation', ...) or None.
    """
    name = st.text_input("Location", value=default, key=f"{prefix}_ort",
                         help="City name, e.g. Madison, Istanbul, Berlin")
    ort = None
    if len(name.strip()) >= 2:
        try:
            treffer = suche_ort(name.strip())
        except requests.RequestException:
            treffer = []
            st.error("Location lookup failed (no internet connection?).")
        else:
            if not treffer:
                st.warning("Location not found. Try only the city name.")
        if treffer:
            idx = st.selectbox("Select match", range(len(treffer)),
                               format_func=lambda i: ort_label(treffer[i]),
                               key=f"{prefix}_treffer_{name.strip().lower()}")
            ort = treffer[idx]
            text = f"📍 Latitude {ort['latitude']:.2f}°"
            if show_elevation:
                text += f" · Elevation {ort.get('elevation') or 0:.0f} m"
            st.caption(text)
    return ort
