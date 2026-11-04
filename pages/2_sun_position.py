import math

import pandas as pd
import streamlit as st

from solar.angles import (
    cos_zenith, equation_of_time_min, solar_azimuth,
    solar_time_correction_min, sunrise_sunset, sunset_hour_angle, zeit_label,
)
from ui.examples import example_picker
from ui.site import get_site, site_summary
from ui.widgets import show_steps, time_input

st.title("🧭 Sun Position")
st.write("Solar time, declination, hour angle, zenith/altitude, solar azimuth, sunrise, sunset and day length.")
site = get_site()
example_picker("sun")
site_summary(site)

solar, steps = time_input("sp", site, default="10:30")
if solar is None:
    st.stop()

lat, dec, n = site["lat"], site["dec"], site["n"]
w = (solar - 12.0) * 15.0
cz = cos_zenith(lat, dec, w)
tz = math.degrees(math.acos(max(-1.0, min(1.0, cz))))
alpha = 90.0 - tz
gs = solar_azimuth(lat, dec, w)
ws = sunset_hour_angle(lat, dec)
sr, ss_ = sunrise_sunset(lat, dec)
corr = solar_time_correction_min(n, site["lon"], site["lst"]) / 60.0

c = st.columns(4)
c[0].metric("Solar time", zeit_label(solar % 24))
c[1].metric("Hour angle ω", f"{w:.2f}°")
c[2].metric("Zenith θz", f"{tz:.2f}°")
c[3].metric("Altitude αs", f"{alpha:.2f}°")
c = st.columns(4)
c[0].metric("Solar azimuth γs", f"{gs:.2f}°", "west" if gs > 0 else ("east" if gs < 0 else "south"),
            delta_color="off")
c[1].metric("Sunset hour angle ωs", f"{ws:.2f}°")
c[2].metric("Day length N", f"{2 * ws / 15:.2f} h")
c[3].metric("Air mass m", f"{1 / cz:.2f}" if 0 < tz < 70 else "–",
            help="m = 1/cos θz, good approximation for θz ≤ 70°")

st.info(
    f"Sunrise **{zeit_label(sr)}** · sunset **{zeit_label(ss_)}** (solar time)  ·  "
    f"clock (standard) time: **{zeit_label((sr - corr) % 24)}** – **{zeit_label((ss_ - corr) % 24)}**"
)
if alpha < 0:
    st.warning("The sun is below the horizon at this time.")

E = equation_of_time_min(n)
steps += [
    ("Declination (Cooper)" if site["dec_method"] == "Cooper" else "Declination (Spencer)",
     rf"\delta = 23.45 \sin\left(360\,\frac{{284+n}}{{365}}\right) = 23.45\sin\left(360\,\frac{{284+{n}}}{{365}}\right) = {dec:.2f}^\circ"
     if site["dec_method"] == "Cooper" else rf"\delta_{{Spencer}}(n={n}) = {dec:.2f}^\circ"),
    ("Hour angle (15° per hour, morning negative)",
     rf"\omega = 15^\circ\,(t_{{solar}} - 12) = 15\,({solar:.3f} - 12) = {w:.2f}^\circ"),
    ("Zenith angle",
     rf"\cos\theta_z = \cos\phi\cos\delta\cos\omega + \sin\phi\sin\delta = {cz:.4f} \Rightarrow \theta_z = {tz:.2f}^\circ,\ \alpha_s = 90^\circ - \theta_z = {alpha:.2f}^\circ"),
    ("Solar azimuth (sign of ω)",
     rf"\gamma_s = \operatorname{{sign}}(\omega)\left|\cos^{{-1}}\frac{{\cos\theta_z\sin\phi - \sin\delta}}{{\sin\theta_z\cos\phi}}\right| = {gs:.2f}^\circ"),
    ("Sunset hour angle and day length",
     rf"\cos\omega_s = -\tan\phi\tan\delta \Rightarrow \omega_s = {ws:.2f}^\circ,\quad N = \tfrac{{2}}{{15}}\omega_s = {2 * ws / 15:.2f}\ \text{{h}}"),
    ("Sunrise / sunset (solar time)",
     rf"t = 12 \mp \frac{{\omega_s}}{{15}} = {sr:.2f}\ \text{{h}}\ /\ {ss_:.2f}\ \text{{h}}"),
]
show_steps(steps)

# ---- Sun path of the day
st.subheader("Sun path on this day")
rows = []
t = math.floor(sr * 4) / 4
while t <= ss_ + 0.25:
    om = (t - 12) * 15
    a = 90 - math.degrees(math.acos(max(-1, min(1, cos_zenith(lat, dec, om)))))
    if a >= 0:
        rows.append({"Solar time (h)": round(t, 2), "Altitude αs (°)": round(a, 2),
                     "Azimuth γs (°)": round(solar_azimuth(lat, dec, om), 2)})
    t += 0.25
if rows:
    df = pd.DataFrame(rows)
    c1, c2 = st.columns(2)
    c1.caption("Altitude over the day")
    c1.line_chart(df, x="Solar time (h)", y="Altitude αs (°)", color="#2a78d6", height=260)
    c2.caption("Sky path: altitude vs. azimuth (0 = south)")
    c2.scatter_chart(df, x="Azimuth γs (°)", y="Altitude αs (°)", color="#eb6834", height=260)
