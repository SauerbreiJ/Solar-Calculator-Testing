import pandas as pd
import streamlit as st

from solar.angles import zeit_label
from solar.clear_sky import CLIMATES, berechne_clear_sky_tag
from ui.examples import example_picker
from ui.site import get_site, site_summary
from ui.widgets import COLORS, init

st.title("🌤️ Clear-Sky Radiation (Whole Day)")
st.write(
    "Hourly clear-sky radiation on a horizontal surface (Hottel beam + Liu & Jordan diffuse), "
    "summed from sunrise to sunset."
)
site = get_site()
example_picker("clear")
site_summary(site)
st.caption(f"Elevation from the sidebar: {site['elev']:.0f} m")

init("cs_climate", "Midlatitude summer")
st.selectbox("Climate type", list(CLIMATES.keys()), key="cs_climate")

dec, sr, ss, rows, h_b, h_d = berechne_clear_sky_tag(site["lat"], site["elev"] / 1000.0, site["n"],
                                                     st.session_state["cs_climate"])
if site["dec_method"] != "Cooper":
    st.caption("Note: this page always uses the Cooper declination.")
if not rows:
    st.warning("No sunrise on this day at this latitude (polar night).")
    st.stop()

h_c = h_b + h_d
st.info(
    f"Declination **{dec:.2f}°** · Sunrise **{zeit_label(sr)}** · "
    f"Sunset **{zeit_label(ss)}** · Day length **{ss - sr:.2f} h** (solar time)"
)
m1, m2, m3 = st.columns(3)
m1.metric("Beam H_cb", f"{h_b:.2f} MJ/m²")
m2.metric("Diffuse H_cd", f"{h_d:.2f} MJ/m²", f"{100 * h_d / h_c:.1f} % of total", delta_color="off")
m3.metric("Total H_c", f"{h_c:.2f} MJ/m²", f"{h_c / 3.6:.2f} kWh/m²", delta_color="off")

df = pd.DataFrame(rows)
chart = df.set_index("Time (solar)")[["I_cb (MJ/m²)", "I_cd (MJ/m²)"]].rename(
    columns={"I_cb (MJ/m²)": "Beam", "I_cd (MJ/m²)": "Diffuse"})
st.bar_chart(chart, color=[COLORS["Beam"], COLORS["Diffuse"]], y_label="MJ/m² per hour")
st.dataframe(df, hide_index=True)
