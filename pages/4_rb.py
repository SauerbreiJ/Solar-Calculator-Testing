import math

import pandas as pd
import streamlit as st

from solar.angles import cos_incidence, cos_zenith, rb_hour_average, rb_instant, rb_noon_south
from ui.examples import example_picker
from ui.site import get_site, site_summary
from ui.widgets import fmt, hour_select, init, show_steps, time_input

st.title("📐 Beam Ratio Rb")
st.write("Rb = ratio of beam radiation on the tilted surface to beam radiation on the horizontal.")
site = get_site()
example_picker("rb")
site_summary(site, surface=True)

lat, dec, b, g = site["lat"], site["dec"], site["slope"], site["azimuth"]
init("rb_mode", "Instantaneous")
mode = st.radio("Calculation", ["Instantaneous", "Hour average", "Solar noon (equator-facing)"],
                key="rb_mode", horizontal=True)

if mode == "Instantaneous":
    solar, steps = time_input("rb", site, default="10:30")
    if solar is None:
        st.stop()
    w = (solar - 12) * 15
    ct, cz = cos_incidence(lat, dec, w, b, g), cos_zenith(lat, dec, w)
    rb = rb_instant(lat, dec, w, b, g)
    c = st.columns(3)
    c[0].metric("cos θ", f"{ct:.4f}")
    c[1].metric("cos θz", f"{cz:.4f}")
    c[2].metric("Rb", fmt(rb, 3))
    if rb is None:
        st.warning("Sun below the horizon – Rb is not defined.")
    elif cz < 0.1:
        st.warning("Sun is close to the horizon: the instantaneous Rb becomes very large. "
                   "Use the hour average for hourly calculations.")
    steps += [
        ("Hour angle", rf"\omega = 15\,({solar:.3f}-12) = {w:.2f}^\circ"),
        ("Angle of incidence on the surface", rf"\cos\theta = {ct:.4f}"),
        ("Zenith angle", rf"\cos\theta_z = \cos\phi\cos\delta\cos\omega + \sin\phi\sin\delta = {cz:.4f}"),
        ("Ratio", rf"R_b = \frac{{\cos\theta}}{{\cos\theta_z}} = \frac{{{ct:.4f}}}{{{cz:.4f}}} = {fmt(rb, 3)}"),
    ]
    show_steps(steps)

elif mode == "Hour average":
    h = hour_select("rb_hour", default=9)
    r = rb_hour_average(lat, dec, (h - 12) * 15.0, (h - 11) * 15.0, b, g)
    mid = (h + 0.5 - 12) * 15
    inst = rb_instant(lat, dec, mid, b, g)
    c = st.columns(3)
    c[0].metric("Rb,ave = a / b", fmt(r["rb"], 3))
    c[1].metric("Rb at the midpoint", fmt(inst, 3), help="Instantaneous value at the middle of the hour")
    c[2].metric("Limits ω1 … ω2", f"{r['w1']:.1f}° … {r['w2']:.1f}°")
    if r["rb"] is None:
        st.warning("The sun is below the horizon during this hour.")
    if r["w1"] > (h - 12) * 15.0 + 1e-6 or r["w2"] < (h - 11) * 15.0 - 1e-6:
        st.info(f"The hour contains sunrise or sunset, so the limits were clipped to ±ωs = ±{r['ws']:.2f}°.")
    if r["numeric"]:
        st.info("The sun is behind the surface for part of this hour; a is integrated numerically over max(cos θ, 0).")
    steps = [
        ("Integration limits (clipped to sunrise/sunset)",
         rf"\omega_1 = {r['w1']:.2f}^\circ,\quad \omega_2 = {r['w2']:.2f}^\circ,\quad \omega_s = {r['ws']:.2f}^\circ"),
        ("Numerator a",
         r"a = (\sin\delta\sin\phi\cos\beta - \sin\delta\cos\phi\sin\beta\cos\gamma)\tfrac{\pi}{180}(\omega_2-\omega_1) "
         r"+ (\cos\delta\cos\phi\cos\beta + \cos\delta\sin\phi\sin\beta\cos\gamma)(\sin\omega_2-\sin\omega_1) "
         rf"- (\cos\delta\sin\beta\sin\gamma)(\cos\omega_2-\cos\omega_1) = {r['a']:.5f}"),
        ("Denominator b",
         rf"b = \cos\phi\cos\delta(\sin\omega_2-\sin\omega_1) + \tfrac{{\pi}}{{180}}(\omega_2-\omega_1)\sin\phi\sin\delta = {r['b']:.5f}"),
        ("Ratio", rf"R_{{b,ave}} = a/b = {fmt(r['rb'], 3)}"),
    ]
    show_steps(steps)

else:
    rb = rb_noon_south(lat, dec, b)
    st.metric("Rb at solar noon", f"{rb:.3f}")
    st.caption("Surface facing the equator (γ = 0° in the northern, 180° in the southern hemisphere). "
               "The surface azimuth from the sidebar is not used here.")
    if lat >= 0:
        tex = (rf"R_{{b,noon}} = \frac{{\cos|\phi-\delta-\beta|}}{{\cos|\phi-\delta|}} = "
               rf"\frac{{\cos|{lat:.2f}-({dec:.2f})-{b:.1f}|}}{{\cos|{lat:.2f}-({dec:.2f})|}} = {rb:.3f}")
    else:
        tex = (rf"R_{{b,noon}} = \frac{{\cos|-\phi+\delta-\beta|}}{{\cos|-\phi+\delta|}} = {rb:.3f}")
    show_steps([("Noon shortcut", tex)], expanded=True)

# ---- Rb over the whole day
with st.expander("📈 Hour-averaged Rb for every hour of this day"):
    rows = []
    for h in range(24):
        r = rb_hour_average(lat, dec, (h - 12) * 15.0, (h - 11) * 15.0, b, g)
        if r["rb"] is not None:
            rows.append({"Hour": f"{h:02d}–{h + 1:02d}", "Rb,ave": round(r["rb"], 3)})
    if rows:
        df = pd.DataFrame(rows)
        st.bar_chart(df, x="Hour", y="Rb,ave", color="#2a78d6", height=240)
        st.dataframe(df, hide_index=True)
