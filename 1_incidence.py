import streamlit as st

from solar.angles import berechne_solar_incidence_exakt
from ui.location import location_input

st.title("☀️ Solar Incidence Angle Calculator")
st.write("Enter your parameters below and click **Calculate** to find the incidence angle.")

# Latitude: either from a place name or typed in manually.
# This part is outside the form so the list of matches appears immediately.
lat_mode = st.radio("Latitude", ["From place name", "Enter manually"],
                    horizontal=True, key="inc_lat_mode")
ort = None
if lat_mode == "From place name":
    ort = location_input("inc", show_elevation=False)
    latitude = ort["latitude"] if ort else None
else:
    latitude = st.number_input("Latitude (°)", min_value=-90.0, max_value=90.0,
                               value=43.0, format="%.2f", key="inc_lat_manual")

with st.form("solar_form"):
    col1, col2 = st.columns(2)

    with col1:
        declination = st.number_input("Declination (°)", value=-14.0, format="%.2f")
        hour_angle = st.number_input("Hour Angle (°)", value=-22.5, format="%.2f")

    with col2:
        slope_angle = st.number_input("Slope Angle / Tilt (°)", value=45.0, format="%.2f")
        surface_azimuth = st.number_input("Surface Azimuth (°)", value=15.0, format="%.2f")

    submitted = st.form_submit_button("Calculate Angle")

if submitted:
    if latitude is None:
        st.error("Please enter a valid location or switch to manual latitude.")
        st.stop()
    result = berechne_solar_incidence_exakt(declination, hour_angle, slope_angle, surface_azimuth, latitude)
    st.success(f"**Calculated Incidence Angle:** {result:.4f}°  (latitude used: {latitude:.2f}°)")
