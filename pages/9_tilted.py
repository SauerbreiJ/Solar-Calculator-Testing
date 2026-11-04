import pandas as pd
import streamlit as st

from solar.chain import hour_from_hourly
from ui.examples import example_picker
from ui.site import get_site, site_summary
from ui.widgets import COLORS, fmt, hour_select, init, show_steps

st.title("📊 Radiation on a Tilted Surface")
st.write("One hour on the tilted surface from horizontal measurements: isotropic sky (Liu & Jordan) vs. "
         "anisotropic sky (HDKR).")
site = get_site()
example_picker("tilted")
site_summary(site, surface=True)
lat, n, dec = site["lat"], site["n"], site["dec"]
b, g, rho = site["slope"], site["azimuth"], site["rho"]

init("tl_I", 1.04)
init("tl_diff_mode", "Estimate with Erbs")
c1, c2 = st.columns(2)
with c1:
    h = hour_select("tl_hour", default=9)
c2.number_input("Hourly total on horizontal I (MJ/m²)", 0.0, 6.0, step=0.01, format="%.3f", key="tl_I")
st.radio("Diffuse part I_d", ["Estimate with Erbs", "Enter measured value"], key="tl_diff_mode", horizontal=True)
Id_in = None
if st.session_state["tl_diff_mode"] == "Enter measured value":
    init("tl_Id", 0.5)
    st.number_input("Hourly diffuse on horizontal I_d (MJ/m²)", 0.0, 6.0, step=0.01, format="%.3f", key="tl_Id")
    Id_in = st.session_state["tl_Id"]

I = st.session_state["tl_I"]
if Id_in is not None and Id_in > I:
    st.error("I_d cannot be larger than I.")
    st.stop()
r = hour_from_hourly(lat, n, h, I, b, g, rho, Id=Id_in, declination=dec)
if r["Io"] <= 0 or r["rb"]["rb"] is None:
    st.warning("The sun is below the horizon during this hour.")
    st.stop()
iso, hd = r["iso"], r["hdkr"]

st.markdown(f"**Horizontal:** I = {I:.3f} · I_o = {r['Io']:.3f} · k_T = {fmt(r['kt'])} · "
            f"I_d = {r['Id']:.3f} · I_b = {r['Ib']:.3f} · R_b = {r['rb']['rb']:.3f}  (MJ/m²)")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Isotropic sky")
    st.metric("I_T", f"{iso['total']:.3f} MJ/m²", f"R = I_T/I = {iso['R']:.3f}", delta_color="off")
with c2:
    st.subheader("HDKR (anisotropic)")
    st.metric("I_T", f"{hd['total']:.3f} MJ/m²", f"R = I_T/I = {hd['R']:.3f}", delta_color="off")
    st.caption(f"A_i = {hd['Ai']:.3f} · f = {hd['f']:.3f}")

comp = pd.DataFrame({
    "Model": ["Isotropic", "HDKR"],
    "Beam": [iso["beam"], hd["beam"]],
    "Circumsolar": [0.0, hd["circumsolar"]],
    "Diffuse": [iso["diffuse"], hd["diffuse"]],
    "Ground-reflected": [iso["ground"], hd["ground"]],
}).set_index("Model")
st.bar_chart(comp, horizontal=True, color=[COLORS[c] for c in comp.columns], x_label="MJ/m²", height=220)
st.dataframe(comp.round(3).assign(Total=comp.sum(axis=1).round(3)))

fs, fg = iso["f_sky"], iso["f_gnd"]
rbv = r["rb"]["rb"]
steps = [
    ("Extraterrestrial radiation and clearness index",
     rf"I_o = {r['Io']:.3f}\ \mathrm{{MJ/m^2}},\quad k_T = I/I_o = {fmt(r['kt'])}"),
    ("Diffuse and beam on the horizontal" + (" (Erbs)" if Id_in is None else " (given)"),
     rf"I_d = {r['Id']:.3f},\quad I_b = I - I_d = {r['Ib']:.3f}\ \mathrm{{MJ/m^2}}"),
    ("Hour-averaged R_b", rf"R_b = a/b = {r['rb']['a']:.4f}/{r['rb']['b']:.4f} = {rbv:.3f}"),
    ("View factors", rf"\frac{{1+\cos\beta}}{{2}} = {fs:.3f},\quad \frac{{1-\cos\beta}}{{2}} = {fg:.3f}"),
    ("Isotropic sky",
     rf"I_T = I_bR_b + I_d\frac{{1+\cos\beta}}{{2}} + I\rho_g\frac{{1-\cos\beta}}{{2}} = "
     rf"{iso['beam']:.3f} + {iso['diffuse']:.3f} + {iso['ground']:.3f} = {iso['total']:.3f}\ \mathrm{{MJ/m^2}}"),
    ("HDKR indices", rf"A_i = \frac{{I_b}}{{I_o}} = {hd['Ai']:.4f},\quad f = \sqrt{{\frac{{I_b}}{{I}}}} = {hd['f']:.4f}"),
    ("HDKR",
     r"I_T = (I_b + I_dA_i)R_b + I_d(1-A_i)\frac{1+\cos\beta}{2}\left[1+f\sin^3\frac{\beta}{2}\right] + I\rho_g\frac{1-\cos\beta}{2}"),
    ("HDKR result",
     rf"I_T = {hd['beam'] + hd['circumsolar']:.3f} + {hd['diffuse']:.3f} + {hd['ground']:.3f} = {hd['total']:.3f}\ \mathrm{{MJ/m^2}}"),
]
show_steps(steps)
