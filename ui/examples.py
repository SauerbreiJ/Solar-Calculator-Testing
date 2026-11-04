"""Lecture examples (ESE 5509, Weeks 2–4) that can be loaded into a page with one click.

Each example sets sidebar keys (site_*, surf_*) and page keys, then reruns the app.
The expected answer from the slides is shown so you can check the result.
"""
import datetime

import streamlit as st


def _site(lat, date, lon=0.0, lst=0.0, elev=0.0, slope=None, azimuth=0.0, rho=0.2):
    v = {"site_mode": "Enter manually", "site_lat": lat, "site_lon": lon, "site_lst": lst,
         "site_elev": elev, "site_date": date, "site_dec_method": "Cooper (lecture)",
         "surf_azimuth": azimuth, "surf_rho": rho}
    if slope is not None:
        v["surf_slope"] = slope
    return v


D = datetime.date

EXAMPLES = {
    "sun": {
        "W2 Ex.2 – Solar time, Madison, 3 Feb, 10:30 CST": (
            {**_site(43.0, D(2026, 2, 3), lon=-89.4, lst=-90.0), "sp_tmode": "Clock time",
             "sp_time": "10:30", "sp_dst": False},
            "Solar time = 10:19"),
        "W2 Ex.4a – Zenith angle, φ = 43°, 13 Feb, 9:30": (
            {**_site(43.0, D(2026, 2, 13)), "sp_tmode": "Solar time", "sp_time": "9:30"},
            "θz = 66.5°"),
        "W2 Ex.4b – Zenith angle, φ = 43°, 1 Jul, 18:30": (
            {**_site(43.0, D(2026, 7, 1)), "sp_tmode": "Solar time", "sp_time": "18:30"},
            "θz = 79.6°"),
        "W2 Ex.5 – Altitude/azimuth, φ = 40°, 16 Jun, 14:00": (
            {**_site(40.0, D(2026, 6, 16)), "sp_tmode": "Solar time", "sp_time": "14:00"},
            "α = 59.75°, γs = 65.67°, day length 14.83 h, sunrise 04:36, sunset 19:24"),
    },
    "incidence": {
        "W2 Ex.3 – Madison, 13 Feb, 10:30, β = 45°, γ = 15°": (
            {**_site(43.0, D(2026, 2, 13), slope=45.0, azimuth=15.0), "inc_tmode": "Solar time",
             "inc_time": "10:30", "inc_override": False},
            "θ = 35° (slides use δ = −14°, ω = −22.5°)"),
    },
    "rb": {
        "W2 Ex.6 – Rb for the surface of Ex.3": (
            {**_site(43.0, D(2026, 2, 13), slope=45.0, azimuth=15.0), "rb_mode": "Instantaneous",
             "rb_time": "10:30"},
            "Rb = 1.67"),
        "W2 Ex.7 – φ = 40°, β = 30° south, 16 Feb, hour 9–10": (
            {**_site(40.0, D(2026, 2, 16), slope=30.0), "rb_mode": "Instantaneous", "rb_time": "9:30"},
            "Rb = 1.61 (at the midpoint 9:30)"),
        "W4 Ex.1 – φ = 45°, β = 60° south, 4 Mar, 6:30 and hour 6–7": (
            {**_site(45.0, D(2026, 3, 4), slope=60.0), "rb_mode": "Hour average", "rb_hour": 6},
            "Rb at 6:30 is huge (≈ 44, sun just above the horizon); the hour average Rb,ave ≈ 4.6"),
    },
    "extra": {
        "W2 Ex.8 – Ho, φ = 43°, 15 Apr": (
            {**_site(43.0, D(2026, 4, 15)), "et_hour": 10}, "Ho = 33.8 MJ/m²"),
        "W2 Ex.9 – Io, φ = 43°, 15 Apr, 10–11 h": (
            {**_site(43.0, D(2026, 4, 15)), "et_hour": 10}, "Io = 3.79 MJ/m²"),
    },
    "clear": {
        "W3 Ex.2/3 – Madison (270 m), 22 Aug, midlatitude summer": (
            {**_site(43.0, D(2026, 8, 22), lon=-89.4, lst=-90.0, elev=270.0),
             "cs_climate": "Midlatitude summer"},
            "Hour 11–12: G_cb ≈ 702 W/m² (2.53 MJ/m²); whole clear day ≈ 22.8 MJ/m²"),
    },
    "split": {
        "W3 Ex.4 – St. Louis (38.6°), 3 Sep, H = 23.0 MJ/m²": (
            {**_site(38.6, D(2026, 9, 3)), "spl_mode": "Daily (Hd/H)", "spl_H": 23.0},
            "K_T ≈ 0.70, Hd/H ≈ 0.24–0.25, Hd ≈ 5.6 MJ/m²"),
        "W4 Ex.2 – φ = 40°, 20 Feb, 9–10 h, I = 1.04 MJ/m²": (
            {**_site(40.0, D(2026, 2, 20)), "spl_mode": "Hourly (Id/I)", "spl_I": 1.04, "spl_hour": 9},
            "Io = 2.34, k_T = 0.445, Id/I = 0.766, Id = 0.80 MJ/m²"),
    },
    "hourly": {
        "W3 Ex.5 – Melbourne (−37.8°), January, 8–9 h": (
            {**_site(-37.8, D(2026, 1, 17)), "dh_H": 25.0, "dh_hour": 8},
            "r_t ≈ 0.075 (fraction of the day's total in 8–9 h)"),
        "W3 Ex.6 – Madison, 23 Aug, H = 31.4 MJ/m², 13–14 h": (
            {**_site(43.0, D(2026, 8, 23)), "dh_H": 31.4, "dh_hour": 13},
            "r_t ≈ 0.118, I ≈ 3.7 MJ/m²"),
    },
    "tilted": {
        "W4 Ex.2/3 – φ = 40°, 20 Feb, 9–10 h, β = 60°, I = 1.04, ρg = 0.6": (
            {**_site(40.0, D(2026, 2, 20), slope=60.0, rho=0.6), "tl_I": 1.04, "tl_hour": 9,
             "tl_diff_mode": "Estimate with Erbs"},
            "Isotropic: I_T ≈ 1.17 MJ/m² · HDKR: A_i = 0.104, I_T ≈ 1.28 MJ/m²"),
    },
}


def _load(page, name):
    """Button callback: runs BEFORE the next script run, so widget values may be changed."""
    values, _ = EXAMPLES[page][name]
    for k, v in values.items():
        st.session_state[k] = v
    st.session_state[f"_loaded_example_{page}"] = name


def example_picker(page):
    """Expander with the lecture examples of one page."""
    examples = EXAMPLES.get(page, {})
    if not examples:
        return
    loaded_key = f"_loaded_example_{page}"
    with st.expander("📚 Load a lecture example", expanded=False):
        name = st.selectbox("Example", list(examples), key=f"_ex_select_{page}",
                            label_visibility="collapsed")
        st.button("Load example", key=f"_ex_btn_{page}", type="primary",
                  on_click=_load, args=(page, name))
    name = st.session_state.get(loaded_key)
    if name in examples:
        st.info(f"📚 **{name}** loaded · expected answer from the slides: **{examples[name][1]}**")
