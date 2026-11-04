import pandas as pd
import streamlit as st

from solar.chain import day_from_daily
from solar.split import erbs_daily_branch
from ui.site import get_site, site_summary
from ui.widgets import COLORS, init

st.title("🔗 Full Chain: Daily H → Tilted Surface")
st.write("All steps of Weeks 2–4 in one go: measured daily total on the horizontal → clearness index → "
         "diffuse part → hourly values → R_b → radiation on the tilted surface.")
site = get_site()
site_summary(site, surface=True)
lat, n, dec = site["lat"], site["n"], site["dec"]
b, g, rho = site["slope"], site["azimuth"], site["rho"]

init("fc_H", 20.0)
st.number_input("Measured daily total on the horizontal H (MJ/m²)", 0.0, 45.0, step=0.1, format="%.2f", key="fc_H")
H = st.session_state["fc_H"]
d = day_from_daily(lat, n, H, b, g, rho, declination=dec)
if not d["hours"] or d["H0"] <= 0:
    st.warning("Polar night – no sun on this day.")
    st.stop()
if d["KT"] > 1:
    st.error(f"K_T = {d['KT']:.2f} > 1: H is larger than the extraterrestrial radiation H_o = {d['H0']:.2f} MJ/m².")
    st.stop()

st.markdown("#### ① Sun geometry and extraterrestrial radiation")
c = st.columns(3)
c[0].metric("δ", f"{dec:.2f}°")
c[1].metric("ω_s", f"{d['ws']:.2f}°")
c[2].metric("H_o", f"{d['H0']:.2f} MJ/m²")

st.markdown("#### ② Clearness index and diffuse part (Erbs, daily)")
c = st.columns(3)
c[0].metric("K_T = H/H_o", f"{d['KT']:.3f}")
c[1].metric("H_d/H", f"{d['diff_frac']:.3f}")
c[2].metric("H_d", f"{d['Hd']:.2f} MJ/m²")
st.caption(f"Branch used: {erbs_daily_branch(d['KT'], d['ws'])}")

st.markdown("#### ③ Hourly values (r_t, r_d) and ④ tilted surface (R_b, isotropic, HDKR)")
rows = [{
    "Hour": f"{x['start']:02d}–{x['start'] + 1:02d}",
    "r_t": round(x["rt"], 4), "r_d": round(x["rd"], 4),
    "I": round(x["I"], 3), "I_d": round(x["Id"], 3), "I_b": round(x["Ib"], 3),
    "I_o": round(x["Io"], 3), "R_b": round(x["rb"], 3),
    "I_T iso": round(x["iso"]["total"], 3), "I_T HDKR": round(x["hdkr"]["total"], 3),
} for x in d["hours"]]
df = pd.DataFrame(rows)
st.dataframe(df, hide_index=True, width="stretch")
st.caption("All energies in MJ/m² per hour. r_t and r_d are evaluated at the midpoint of each hour.")

st.markdown("#### ⑤ Daily totals")
sum_h = df["I"].sum()
c = st.columns(3)
c[0].metric("Horizontal (Σ I)", f"{sum_h:.2f} MJ/m²", help="Close to H; small differences come from the hour-midpoint method")
c[1].metric("Tilted, isotropic", f"{d['HT_iso']:.2f} MJ/m²", f"{100 * (d['HT_iso'] / sum_h - 1):+.1f} % vs. horizontal",
            delta_color="off")
c[2].metric("Tilted, HDKR", f"{d['HT_hdkr']:.2f} MJ/m²", f"{100 * (d['HT_hdkr'] / sum_h - 1):+.1f} % vs. horizontal",
            delta_color="off")

comp = pd.DataFrame({
    "Hour": df["Hour"],
    "Beam": [x["hdkr"]["beam"] for x in d["hours"]],
    "Circumsolar": [x["hdkr"]["circumsolar"] for x in d["hours"]],
    "Diffuse": [x["hdkr"]["diffuse"] for x in d["hours"]],
    "Ground-reflected": [x["hdkr"]["ground"] for x in d["hours"]],
}).set_index("Hour")
st.caption("HDKR components on the tilted surface, per hour (MJ/m²)")
st.bar_chart(comp, color=[COLORS[c] for c in comp.columns], y_label="MJ/m² per hour")

st.info("To see every formula with numbers for one hour, open **Tilted Surface**, choose the hour and enter "
        "the I value from the table above.")
