import math

import streamlit as st

from solar.angles import cos_incidence, cos_zenith
from ui.examples import example_picker
from ui.site import get_site, site_summary
from ui.widgets import init, show_steps, time_input

st.title("☀️ Angle of Incidence")
st.write("Angle θ between the beam radiation and the normal of a tilted surface.")
site = get_site()
example_picker("incidence")
site_summary(site, surface=True)

solar, steps = time_input("inc", site, default="10:30")
if solar is None:
    st.stop()

init("inc_override", False)
st.checkbox("Enter δ and ω directly (e.g. values given in an exam question)", key="inc_override")
dec, w = site["dec"], (solar - 12) * 15
if st.session_state["inc_override"]:
    init("inc_dec", round(dec, 2))
    init("inc_w", round(w, 2))
    c1, c2 = st.columns(2)
    c1.number_input("Declination δ (°)", -23.45, 23.45, step=0.5, format="%.2f", key="inc_dec")
    c2.number_input("Hour angle ω (°)", -180.0, 180.0, step=7.5, format="%.2f", key="inc_w")
    dec, w = st.session_state["inc_dec"], st.session_state["inc_w"]

lat, b, g = site["lat"], site["slope"], site["azimuth"]
ct = cos_incidence(lat, dec, w, b, g)
theta = math.degrees(math.acos(max(-1.0, min(1.0, ct))))
cz = cos_zenith(lat, dec, w)
tz = math.degrees(math.acos(max(-1.0, min(1.0, cz))))

c = st.columns(3)
c[0].metric("Angle of incidence θ", f"{theta:.2f}°")
c[1].metric("Zenith angle θz", f"{tz:.2f}°")
c[2].metric("Rb = cos θ / cos θz", f"{max(ct, 0) / cz:.3f}" if cz > 0 else "–")
if ct < 0:
    st.warning("cos θ < 0: the sun is behind the surface – no beam radiation reaches it.")
if cz <= 0:
    st.warning("The sun is below the horizon.")

steps += [
    ("Inputs", rf"\phi = {lat:.2f}^\circ,\ \delta = {dec:.2f}^\circ,\ \omega = {w:.2f}^\circ,\ \beta = {b:.1f}^\circ,\ \gamma = {g:.1f}^\circ"),
    ("Angle of incidence (general equation)",
     r"\cos\theta = \sin\delta\sin\phi\cos\beta - \sin\delta\cos\phi\sin\beta\cos\gamma "
     r"+ \cos\delta\cos\phi\cos\beta\cos\omega + \cos\delta\sin\phi\sin\beta\cos\gamma\cos\omega "
     r"+ \cos\delta\sin\beta\sin\gamma\sin\omega"),
    ("Result", rf"\cos\theta = {ct:.4f} \Rightarrow \theta = {theta:.2f}^\circ"),
]
show_steps(steps)
