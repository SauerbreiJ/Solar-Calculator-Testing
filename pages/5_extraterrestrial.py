import math

import pandas as pd
import streamlit as st

from solar.angles import MEAN_DAY_OF_MONTH, declination_deg, sunset_hour_angle
from solar.extraterrestrial import (
    GSC, daily_extraterrestrial, extraterrestrial_normal, hourly_extraterrestrial, spectral_split,
)
from solar.sunshine import MONTHS
from ui.examples import example_picker
from ui.site import get_site, site_summary
from ui.widgets import hour_select, show_steps

st.title("🌍 Extraterrestrial Radiation")
st.write("Radiation at the top of the atmosphere: G_on (normal), H_o (day, horizontal), I_o (hour, horizontal).")
site = get_site()
example_picker("extra")
site_summary(site)

lat, dec, n = site["lat"], site["dec"], site["n"]
ws = sunset_hour_angle(lat, dec)
gon = extraterrestrial_normal(n)
h0 = daily_extraterrestrial(lat, n, dec)
h = hour_select("et_hour", default=10)
i0 = hourly_extraterrestrial(lat, n, (h - 12) * 15.0, (h - 11) * 15.0, dec)

c = st.columns(3)
c[0].metric("G_on", f"{gon:.1f} W/m²")
c[1].metric("H_o (day)", f"{h0:.2f} MJ/m²", f"{h0 / 3.6:.2f} kWh/m²", delta_color="off")
c[2].metric(f"I_o ({h:02d}–{h + 1:02d} h)", f"{i0:.3f} MJ/m²")

w1, w2 = max((h - 12) * 15.0, -ws), min((h - 11) * 15.0, ws)
show_steps([
    ("Normal extraterrestrial irradiance",
     rf"G_{{on}} = G_{{sc}}\left(1+0.033\cos\frac{{360\,n}}{{365}}\right) = 1367\left(1+0.033\cos\frac{{360\cdot{n}}}{{365}}\right) = {gon:.1f}\ \mathrm{{W/m^2}}"),
    ("Sunset hour angle", rf"\cos\omega_s = -\tan\phi\tan\delta \Rightarrow \omega_s = {ws:.2f}^\circ"),
    ("Daily H_o",
     rf"H_o = \frac{{24\cdot3600\,G_{{sc}}}}{{\pi}}\left(1+0.033\cos\frac{{360n}}{{365}}\right)"
     rf"\left(\cos\phi\cos\delta\sin\omega_s + \frac{{\pi\omega_s}}{{180}}\sin\phi\sin\delta\right) = {h0:.2f}\ \mathrm{{MJ/m^2}}"),
    ("Hourly I_o (limits clipped to sunrise/sunset)",
     rf"I_o = \frac{{12\cdot3600\,G_{{sc}}}}{{\pi}}\left(1+0.033\cos\frac{{360n}}{{365}}\right)"
     rf"\left(\cos\phi\cos\delta(\sin\omega_2-\sin\omega_1) + \frac{{\pi(\omega_2-\omega_1)}}{{180}}\sin\phi\sin\delta\right),"
     rf"\ \omega_1={w1:.1f}^\circ,\ \omega_2={w2:.1f}^\circ \Rightarrow I_o = {i0:.3f}\ \mathrm{{MJ/m^2}}"),
])

st.subheader("Monthly mean H̄_o (mean day of each month)")
rows = []
for i, nd in enumerate(MEAN_DAY_OF_MONTH):
    rows.append({"Month": MONTHS[i], "Mean day n": nd, "δ (°)": round(declination_deg(nd), 2),
                 "H̄_o (MJ/m²)": round(daily_extraterrestrial(lat, nd), 2)})
df = pd.DataFrame(rows)
c1, c2 = st.columns([3, 2])
c1.bar_chart(df, x="Month", y="H̄_o (MJ/m²)", color="#2a78d6", height=260, sort=False)
c2.dataframe(df, hide_index=True, height=260)

with st.expander("🌈 Spectral split of the solar constant (Week 2, Example 1)"):
    s = spectral_split()
    st.dataframe(pd.DataFrame([{"Range": k, "Fraction": round(f, 3), "W/m²": round(w, 1)} for k, (f, w) in s.items()]),
                 hide_index=True)
    st.caption(f"f(0–0.38 µm) = 0.064, f(0–0.78 µm) = 0.544 from the WRC table, applied to G_sc = {GSC:.0f} W/m².")
