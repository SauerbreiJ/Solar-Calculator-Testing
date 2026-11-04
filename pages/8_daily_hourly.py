import pandas as pd
import streamlit as st

from solar.angles import declination_deg, sunset_hour_angle
from solar.extraterrestrial import daily_extraterrestrial
from solar.split import collares_pereira_rabl, crp_coefficients, erbs_daily, liu_jordan_rd
from ui.examples import example_picker
from ui.site import get_site, site_summary
from ui.widgets import COLORS, hour_select, init, show_steps

st.title("⏱️ Daily → Hourly Radiation")
st.write("Distribute a daily total over the hours: r_t (Collares-Pereira & Rabl) for the total, "
         "r_d (Liu & Jordan) for the diffuse part.")
site = get_site()
example_picker("hourly")
site_summary(site)
lat, dec, n = site["lat"], site["dec"], site["n"]
ws = sunset_hour_angle(lat, dec)
if ws <= 0:
    st.warning("Polar night.")
    st.stop()

init("dh_H", 31.4)
init("dh_Hd_mode", "Estimate with Erbs (daily)")
c1, c2 = st.columns(2)
c1.number_input("Daily total H (MJ/m²)", 0.0, 45.0, step=0.1, format="%.2f", key="dh_H")
c2.radio("Daily diffuse H_d", ["Estimate with Erbs (daily)", "Enter value"], key="dh_Hd_mode")
H = st.session_state["dh_H"]
h0 = daily_extraterrestrial(lat, n, dec)
KT = H / h0 if h0 > 0 else 0
if st.session_state["dh_Hd_mode"] == "Enter value":
    init("dh_Hd", round(0.3 * H, 2))
    st.number_input("Daily diffuse H_d (MJ/m²)", 0.0, 45.0, step=0.1, format="%.2f", key="dh_Hd")
    Hd = st.session_state["dh_Hd"]
else:
    Hd = erbs_daily(KT, ws) * H
    st.caption(f"K_T = {KT:.3f} → H_d/H = {Hd / H if H else 0:.3f} → H_d = {Hd:.2f} MJ/m²")

h = hour_select("dh_hour", default=13, label="Hour to inspect (solar time)")
mid = (h + 0.5 - 12) * 15
rt, rd = collares_pereira_rabl(mid, ws), liu_jordan_rd(mid, ws)
a, b = crp_coefficients(ws)
c = st.columns(4)
c[0].metric("r_t", f"{rt:.4f}")
c[1].metric("I = r_t·H", f"{rt * H:.3f} MJ/m²")
c[2].metric("r_d", f"{rd:.4f}")
c[3].metric("I_d = r_d·H_d", f"{rd * Hd:.3f} MJ/m²")
if rt == 0:
    st.warning("The midpoint of this hour is before sunrise or after sunset.")

show_steps([
    ("Hour angle at the midpoint of the hour", rf"\omega = 15\,({h + 0.5:.1f}-12) = {mid:.1f}^\circ,\quad \omega_s = {ws:.2f}^\circ"),
    ("Coefficients", rf"a = 0.409 + 0.5016\sin(\omega_s-60) = {a:.4f},\quad b = 0.6609 - 0.4767\sin(\omega_s-60) = {b:.4f}"),
    ("Collares-Pereira & Rabl",
     rf"r_t = \frac{{\pi}}{{24}}(a + b\cos\omega)\frac{{\cos\omega - \cos\omega_s}}{{\sin\omega_s - \frac{{\pi\omega_s}}{{180}}\cos\omega_s}} = {rt:.4f}"),
    ("Liu & Jordan", rf"r_d = \frac{{\pi}}{{24}}\frac{{\cos\omega - \cos\omega_s}}{{\sin\omega_s - \frac{{\pi\omega_s}}{{180}}\cos\omega_s}} = {rd:.4f}"),
    ("Hourly values", rf"I = {rt:.4f}\cdot{H:.2f} = {rt * H:.3f},\quad I_d = {rd:.4f}\cdot{Hd:.2f} = {rd * Hd:.3f},\quad I_b = I - I_d = {rt * H - rd * Hd:.3f}\ \mathrm{{MJ/m^2}}"),
], expanded=False)

st.subheader("All hours of the day")
rows = []
for hh in range(24):
    m = (hh + 0.5 - 12) * 15
    t, d = collares_pereira_rabl(m, ws), liu_jordan_rd(m, ws)
    if t <= 0:
        continue
    I, Id = t * H, min(d * Hd, t * H)
    rows.append({"Hour": f"{hh:02d}–{hh + 1:02d}", "ω (°)": m, "r_t": round(t, 4), "r_d": round(d, 4),
                 "I (MJ/m²)": round(I, 3), "I_d (MJ/m²)": round(Id, 3), "I_b (MJ/m²)": round(I - Id, 3)})
df = pd.DataFrame(rows)
st.bar_chart(df.set_index("Hour")[["I_b (MJ/m²)", "I_d (MJ/m²)"]].rename(
    columns={"I_b (MJ/m²)": "Beam", "I_d (MJ/m²)": "Diffuse"}),
    color=[COLORS["Beam"], COLORS["Diffuse"]], y_label="MJ/m² per hour")
st.dataframe(df, hide_index=True)
st.caption(f"Σ r_t = {df['r_t'].sum():.3f} and Σ r_d = {df['r_d'].sum():.3f} – close to 1, "
           "the small difference comes from evaluating at the hour midpoints.")
