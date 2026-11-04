import streamlit as st

from solar.angles import sunset_hour_angle
from solar.extraterrestrial import daily_extraterrestrial, hourly_extraterrestrial
from solar.split import erbs_daily, erbs_daily_branch, erbs_hourly, erbs_hourly_branch, erbs_monthly
from ui.examples import example_picker
from ui.site import get_site, site_summary
from ui.widgets import hour_select, init, show_steps

st.title("🔀 Beam / Diffuse Split (Erbs et al.)")
st.write("Estimate the diffuse part of the measured total radiation from the clearness index.")
site = get_site()
example_picker("split")
site_summary(site)
lat, dec, n = site["lat"], site["dec"], site["n"]
ws = sunset_hour_angle(lat, dec)

init("spl_mode", "Hourly (Id/I)")
mode = st.radio("Time base", ["Hourly (Id/I)", "Daily (Hd/H)", "Monthly average (H̄d/H̄)"],
                key="spl_mode", horizontal=True)

if mode.startswith("Hourly"):
    init("spl_I", 1.04)
    c1, c2 = st.columns(2)
    with c1:
        h = hour_select("spl_hour", default=9)
    c2.number_input("Measured hourly total I (MJ/m²)", 0.0, 6.0, step=0.01, format="%.3f", key="spl_I")
    I = st.session_state["spl_I"]
    io = hourly_extraterrestrial(lat, n, (h - 12) * 15.0, (h - 11) * 15.0, dec)
    if io <= 0:
        st.warning("The sun is below the horizon during this hour.")
        st.stop()
    kt = I / io
    frac = erbs_hourly(kt)
    c = st.columns(4)
    c[0].metric("I_o", f"{io:.3f} MJ/m²")
    c[1].metric("k_T = I/I_o", f"{kt:.3f}")
    c[2].metric("I_d / I", f"{frac:.3f}")
    c[3].metric("I_d · I_b", f"{frac * I:.3f} · {(1 - frac) * I:.3f}")
    if kt > 1:
        st.error("k_T > 1: the measured value is larger than the extraterrestrial radiation – check the input.")
    show_steps([
        ("Extraterrestrial radiation for the hour", rf"I_o = {io:.3f}\ \mathrm{{MJ/m^2}}"),
        ("Hourly clearness index", rf"k_T = \frac{{I}}{{I_o}} = \frac{{{I:.3f}}}{{{io:.3f}}} = {kt:.3f}"),
        (f"Erbs hourly correlation, branch {erbs_hourly_branch(kt)}",
         r"\frac{I_d}{I} = \begin{cases} 1 - 0.09k_T & k_T \le 0.22 \\ "
         r"0.9511 - 0.1604k_T + 4.388k_T^2 - 16.638k_T^3 + 12.336k_T^4 & 0.22 < k_T \le 0.80 \\ "
         rf"0.165 & k_T > 0.80 \end{{cases}} = {frac:.3f}"),
        ("Components", rf"I_d = {frac:.3f}\cdot{I:.3f} = {frac * I:.3f},\quad I_b = I - I_d = {(1 - frac) * I:.3f}\ \mathrm{{MJ/m^2}}"),
    ], expanded=True)

elif mode.startswith("Daily"):
    init("spl_H", 23.0)
    st.number_input("Measured daily total H (MJ/m²)", 0.0, 45.0, step=0.1, format="%.2f", key="spl_H")
    H = st.session_state["spl_H"]
    h0 = daily_extraterrestrial(lat, n, dec)
    if h0 <= 0:
        st.warning("Polar night.")
        st.stop()
    KT = H / h0
    frac = erbs_daily(KT, ws)
    c = st.columns(4)
    c[0].metric("H_o", f"{h0:.2f} MJ/m²")
    c[1].metric("K_T = H/H_o", f"{KT:.3f}")
    c[2].metric("H_d / H", f"{frac:.3f}")
    c[3].metric("H_d", f"{frac * H:.2f} MJ/m²")
    show_steps([
        ("Sunset hour angle and H_o", rf"\omega_s = {ws:.2f}^\circ,\quad H_o = {h0:.2f}\ \mathrm{{MJ/m^2}}"),
        ("Daily clearness index", rf"K_T = \frac{{H}}{{H_o}} = \frac{{{H:.2f}}}{{{h0:.2f}}} = {KT:.3f}"),
        (f"Erbs daily correlation, branch {erbs_daily_branch(KT, ws)}",
         (r"\frac{H_d}{H} = 1 - 0.2727K_T + 2.4495K_T^2 - 11.9514K_T^3 + 9.3879K_T^4\ (K_T<0.715),\ \text{else } 0.143"
          if ws <= 81.4 else
          r"\frac{H_d}{H} = 1 + 0.2832K_T - 2.5557K_T^2 + 0.8448K_T^3\ (K_T<0.722),\ \text{else } 0.175")
         + rf"\ \Rightarrow\ {frac:.3f}"),
        ("Diffuse and beam", rf"H_d = {frac:.3f}\cdot{H:.2f} = {frac * H:.2f},\quad H_b = {(1 - frac) * H:.2f}\ \mathrm{{MJ/m^2}}"),
    ], expanded=True)

else:
    init("spl_Hbar", 15.0)
    st.number_input("Monthly average daily total H̄ (MJ/m²)", 0.0, 45.0, step=0.1, format="%.2f", key="spl_Hbar")
    st.caption("Tip: set the sidebar date to the mean day of the month (e.g. 17 Jan, 16 Feb, 16 Mar …).")
    H = st.session_state["spl_Hbar"]
    h0 = daily_extraterrestrial(lat, n, dec)
    KT = H / h0 if h0 > 0 else 0
    frac = erbs_monthly(KT, ws)
    c = st.columns(3)
    c[0].metric("K̄_T", f"{KT:.3f}")
    c[1].metric("H̄_d / H̄", f"{frac:.3f}")
    c[2].metric("H̄_d", f"{frac * H:.2f} MJ/m²")
    if not 0.3 <= KT <= 0.8:
        st.warning("The monthly correlation is only valid for 0.3 ≤ K̄_T ≤ 0.8.")
    show_steps([
        ("Clearness index", rf"\bar K_T = {H:.2f}/{h0:.2f} = {KT:.3f},\quad \omega_s = {ws:.2f}^\circ"),
        ("Erbs monthly correlation",
         (r"\frac{\bar H_d}{\bar H} = 1.391 - 3.560\bar K_T + 4.189\bar K_T^2 - 2.137\bar K_T^3\ (\omega_s \le 81.4^\circ)"
          if ws <= 81.4 else
          r"\frac{\bar H_d}{\bar H} = 1.311 - 3.022\bar K_T + 3.427\bar K_T^2 - 1.821\bar K_T^3\ (\omega_s > 81.4^\circ)")
         + rf" = {frac:.3f}"),
    ], expanded=True)
