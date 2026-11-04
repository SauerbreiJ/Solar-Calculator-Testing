"""Shared sidebar inputs (site, date, surface) used by every page.

Called once in app.py BEFORE the page runs, so the values are available on every page
via get_site(). Widgets get their defaults through st.session_state (no value= argument),
so lecture examples can overwrite them (see ui/examples.py).
"""
import datetime
import math
from zoneinfo import ZoneInfo

import streamlit as st

from solar.angles import day_of_year, declination_deg, declination_spencer_deg
from ui.location import location_input

DEFAULTS = {
    "site_mode": "Enter manually",
    "site_lat": 43.0,
    "site_lon": -89.4,
    "site_elev": 270.0,
    "site_lst": -90.0,
    "site_date": datetime.date(2026, 8, 22),
    "site_dec_method": "Cooper (lecture)",
    "surf_slope": 45.0,
    "surf_azimuth": 0.0,
    "surf_rho": 0.20,
}


def _std_meridian_from_tz(tz_name, date):
    """Standard meridian [°, east positive] = 15° × standard UTC offset (DST removed)."""
    try:
        dt = datetime.datetime(date.year, date.month, date.day, 12, tzinfo=ZoneInfo(tz_name))
        hours = (dt.utcoffset() - (dt.dst() or datetime.timedelta(0))).total_seconds() / 3600
        return 15.0 * hours
    except Exception:
        return None


def site_sidebar():
    ss = st.session_state
    for k, v in DEFAULTS.items():
        ss.setdefault(k, v)

    with st.sidebar:
        st.markdown("### 📍 Site")
        st.radio("Location input", ["From place name", "Enter manually"], key="site_mode",
                 horizontal=True, label_visibility="collapsed")
        place = None
        if ss["site_mode"] == "From place name":
            ort = location_input("site", show_elevation=True)
            if ort:
                lst = _std_meridian_from_tz(ort.get("timezone", ""), ss["site_date"])
                place = {
                    "lat": ort["latitude"], "lon": ort["longitude"],
                    "elev": ort.get("elevation") or 0.0,
                    "lst": lst if lst is not None else 15.0 * round(ort["longitude"] / 15.0),
                }
                st.caption(f"Longitude {place['lon']:.2f}° · standard meridian {place['lst']:.0f}°")
            else:
                st.caption("No place selected – the manual values below are used.")
        if place is None:
            c1, c2 = st.columns(2)
            c1.number_input("Latitude φ (°)", -90.0, 90.0, step=0.1, format="%.2f", key="site_lat",
                            help="North positive")
            c2.number_input("Longitude (°)", -180.0, 180.0, step=0.1, format="%.2f", key="site_lon",
                            help="EAST positive (Madison = −89.4, Istanbul = +29.0)")
            c1.number_input("Elevation (m)", -500.0, 9000.0, step=10.0, format="%.0f", key="site_elev")
            c2.number_input("Std. meridian (°)", -180.0, 180.0, step=15.0, format="%.0f", key="site_lst",
                            help="15° × UTC offset of the standard time zone, east positive "
                                 "(Central US = −90, Istanbul = +45, Sweden = +15)")
            place = {"lat": ss["site_lat"], "lon": ss["site_lon"],
                     "elev": ss["site_elev"], "lst": ss["site_lst"]}

        st.markdown("### 📅 Date")
        st.date_input("Date", key="site_date", format="DD.MM.YYYY", label_visibility="collapsed")
        st.radio("Declination formula", ["Cooper (lecture)", "Spencer (more accurate)"],
                 key="site_dec_method", horizontal=True)
        d = ss["site_date"]
        day = 28 if (d.month == 2 and d.day == 29) else d.day
        n = day_of_year(day, d.month)
        cooper = ss["site_dec_method"].startswith("Cooper")
        dec = declination_deg(n) if cooper else declination_spencer_deg(n)
        st.caption(f"Day number **n = {n}** · declination **δ = {dec:.2f}°**")

        st.markdown("### 🏠 Surface")
        c1, c2 = st.columns(2)
        c1.number_input("Slope β (°)", 0.0, 180.0, step=5.0, format="%.1f", key="surf_slope")
        c2.number_input("Azimuth γ (°)", -180.0, 180.0, step=5.0, format="%.1f", key="surf_azimuth",
                        help="0 = facing south, east negative, west positive")
        st.number_input("Ground reflectance ρg", 0.0, 1.0, step=0.05, format="%.2f", key="surf_rho",
                        help="≈ 0.2 grass / concrete, ≈ 0.7 fresh snow")

    site = {**place, "n": n, "dec": dec, "date": d, "dec_method": "Cooper" if cooper else "Spencer",
            "slope": ss["surf_slope"], "azimuth": ss["surf_azimuth"], "rho": ss["surf_rho"]}
    ss["site"] = site
    return site


def get_site():
    """Current sidebar values (dict)."""
    return st.session_state["site"]


def site_summary(site, surface=False):
    """One-line caption so every page shows which sidebar values it uses."""
    text = (f"Using sidebar values: φ = {site['lat']:.2f}°, n = {site['n']} "
            f"({site['date']:%d %b}), δ = {site['dec']:.2f}° ({site['dec_method']})")
    if surface:
        text += f" · β = {site['slope']:.1f}°, γ = {site['azimuth']:.1f}°, ρg = {site['rho']:.2f}"
    st.caption("⚙️ " + text + " — change them in the sidebar.")
