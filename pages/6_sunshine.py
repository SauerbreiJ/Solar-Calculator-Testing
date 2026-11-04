import pandas as pd
import streamlit as st

from solar.angles import MEAN_DAY_OF_MONTH, day_length, declination_deg
from solar.extraterrestrial import daily_extraterrestrial
from solar.sunshine import MONTHS, PRESETS, angstrom_prescott, monthly_table
from ui.site import get_site
from ui.widgets import init, show_steps

st.title("🌥️ Average Radiation from Sunshine Hours")
st.write("Angström-Prescott: estimate the monthly average daily radiation H̄ from the average sunshine hours n̄.")
site = get_site()
lat = site["lat"]
st.caption(f"⚙️ Using sidebar latitude φ = {lat:.2f}°. Each month is evaluated at its mean day (n̄).")

init("ss_preset", list(PRESETS)[0])
st.selectbox("Coefficients a, b", list(PRESETS), key="ss_preset")
preset = PRESETS[st.session_state["ss_preset"]]
init("ss_a", 0.25)
init("ss_b", 0.50)
if preset is not None:
    st.session_state["ss_a"], st.session_state["ss_b"] = preset
c1, c2 = st.columns(2)
c1.number_input("a", 0.0, 1.0, step=0.01, format="%.2f", key="ss_a", disabled=preset is not None)
c2.number_input("b", 0.0, 1.0, step=0.01, format="%.2f", key="ss_b", disabled=preset is not None)
a, b = st.session_state["ss_a"], st.session_state["ss_b"]

init("ss_mode", "One month")
mode = st.radio("Input", ["One month", "All 12 months"], key="ss_mode", horizontal=True)

if mode == "One month":
    init("ss_month", 0)
    init("ss_hours", 5.0)
    c1, c2 = st.columns(2)
    m = c1.selectbox("Month", range(12), key="ss_month", format_func=lambda i: MONTHS[i])
    c2.number_input("Average sunshine hours n̄ (h/day)", 0.0, 24.0, step=0.1, format="%.1f", key="ss_hours")
    n = MEAN_DAY_OF_MONTH[m]
    dec = declination_deg(n)
    N = day_length(lat, dec)
    h0 = daily_extraterrestrial(lat, n)
    nb = st.session_state["ss_hours"]
    if N <= 0:
        st.warning("Polar night – no sunshine possible.")
        st.stop()
    if nb > N:
        st.error(f"n̄ cannot be larger than the day length N̄ = {N:.2f} h.")
        st.stop()
    H, kt = angstrom_prescott(h0, nb, N, a, b)
    c = st.columns(4)
    c[0].metric("Day length N̄", f"{N:.2f} h")
    c[1].metric("H̄_o", f"{h0:.2f} MJ/m²")
    c[2].metric("K̄_T = H̄/H̄_o", f"{kt:.3f}")
    c[3].metric("H̄", f"{H:.2f} MJ/m²", f"{H / 3.6:.2f} kWh/m²", delta_color="off")
    show_steps([
        ("Mean day and declination", rf"n = {n},\quad \delta = {dec:.2f}^\circ"),
        ("Day length", rf"N̄ = \tfrac{{2}}{{15}}\cos^{{-1}}(-\tan\phi\tan\delta) = {N:.2f}\ \text{{h}}"),
        ("Extraterrestrial radiation", rf"\bar H_o = {h0:.2f}\ \mathrm{{MJ/m^2}}"),
        ("Angström-Prescott",
         rf"\frac{{\bar H}}{{\bar H_o}} = a + b\frac{{\bar n}}{{\bar N}} = {a:.2f} + {b:.2f}\cdot\frac{{{nb:.1f}}}{{{N:.2f}}} = {kt:.3f}"
         rf"\ \Rightarrow\ \bar H = {kt:.3f}\cdot{h0:.2f} = {H:.2f}\ \mathrm{{MJ/m^2}}"),
    ], expanded=True)
else:
    st.write("Enter the average daily sunshine hours for each month (edit the table):")
    init("ss_table", pd.DataFrame({"Month": MONTHS, "n̄ (h/day)": [3.0, 4.0, 5.0, 6.5, 8.0, 9.5,
                                                                  10.0, 9.0, 7.5, 6.0, 3.5, 2.5]}))
    edited = st.data_editor(st.session_state["ss_table"], hide_index=True, disabled=["Month"],
                            key="ss_editor", width="stretch")
    rows = monthly_table(lat, [None if pd.isna(v) else float(v) for v in edited["n̄ (h/day)"]], a, b)
    df = pd.DataFrame([{
        "Month": r["month"], "n": r["n"], "N̄ (h)": round(r["N"], 2),
        "n̄/N̄": None if r["ratio"] is None else round(r["ratio"], 3),
        "H̄_o (MJ/m²)": round(r["H0"], 2),
        "K̄_T": None if r["KT"] is None else round(r["KT"], 3),
        "H̄ (MJ/m²)": None if r["H"] is None else round(r["H"], 2)} for r in rows])
    bad = [r["month"] for r in rows if r["sun"] is not None and r["sun"] > r["N"]]
    if bad:
        st.warning("n̄ is larger than the day length in: " + ", ".join(bad))
    st.dataframe(df, hide_index=True, width="stretch")
    st.bar_chart(df, x="Month", y="H̄ (MJ/m²)", color="#2a78d6", height=260, sort=False)
    st.caption(f"Days per month × H̄ summed → yearly ≈ "
               f"{sum(h * d for h, d in zip(df['H̄ (MJ/m²)'].fillna(0), (31,28,31,30,31,30,31,31,30,31,30,31))) / 3.6:.0f} kWh/m²")
