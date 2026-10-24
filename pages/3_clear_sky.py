import pandas as pd
import requests
import streamlit as st

from solar.angles import zeit_label
from solar.clear_sky import CLIMATES, berechne_clear_sky_tag
from solar.geocoding import finde_ort, ort_label


@st.cache_data(show_spinner=False)
def suche_ort(name):
    """Gecachte Ortssuche, damit derselbe Name nicht bei jedem Klick neu abgefragt wird."""
    return finde_ort(name)


st.title("🌤️ Clear-Sky Radiation (Whole Day)")
st.write(
    "Hourly clear-sky radiation on a horizontal surface (Hottel beam + Liu & Jordan diffuse), "
    "summed from sunrise to sunset."
)

# Ortssuche liegt außerhalb des Formulars, damit die Trefferliste sofort erscheint
cs_ort = st.text_input("Location", value="Madison", key="cs_ort",
                       help="City name, e.g. Madison, Istanbul, Berlin")
ort = None
if len(cs_ort.strip()) >= 2:
    try:
        treffer = suche_ort(cs_ort.strip())
    except requests.RequestException:
        treffer = []
        st.error("Location lookup failed (no internet connection?).")
    else:
        if not treffer:
            st.warning("Location not found. Try only the city name.")
    if treffer:
        idx = st.selectbox("Select match", range(len(treffer)),
                           format_func=lambda i: ort_label(treffer[i]),
                           key=f"cs_treffer_{cs_ort.strip().lower()}")
        ort = treffer[idx]
        st.caption(f"📍 Latitude {ort['latitude']:.2f}° · "
                   f"Elevation {ort.get('elevation') or 0:.0f} m")

with st.form("clear_sky_form"):
    c1, c2 = st.columns(2)
    with c1:
        cs_n = st.number_input("Day of the year n", min_value=1, max_value=365,
                               value=234, step=1, key="cs_n",
                               help="Aug 22 = 234. See the Day & Hour Angle page.")
    with c2:
        cs_climate = st.selectbox("Climate type", list(CLIMATES.keys()),
                                  index=2, key="cs_climate")
    cs_submitted = st.form_submit_button("Calculate Day")

if cs_submitted:
    if ort is None:
        st.error("Please enter a valid location first.")
        st.stop()
    cs_lat = ort["latitude"]
    cs_alt = ort.get("elevation") or 0.0   # Höhe in m (0, falls nicht vorhanden)
    dec, sr, ss, rows, h_b, h_d = berechne_clear_sky_tag(cs_lat, cs_alt / 1000.0, int(cs_n), cs_climate)
    if not rows:
        st.warning("No sunrise on this day at this latitude (polar night).")
    else:
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
        st.dataframe(df, hide_index=True)
        st.bar_chart(df.set_index("Time (solar)")[["I_cb (MJ/m²)", "I_cd (MJ/m²)"]])
