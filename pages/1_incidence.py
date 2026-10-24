import streamlit as st

from solar.angles import berechne_solar_incidence_exakt

st.title("☀️ Solar Incidence Angle Calculator")
st.write("Enter your parameters below and click **Calculate** to find the incidence angle.")

with st.form("solar_form"):
    col1, col2 = st.columns(2)

    with col1:
        declination = st.number_input("Declination (°)", value=-14.0, format="%.2f")
        hour_angle = st.number_input("Hour Angle (°)", value=-22.5, format="%.2f")
        slope_angle = st.number_input("Slope Angle / Tilt (°)", value=45.0, format="%.2f")

    with col2:
        surface_azimuth = st.number_input("Surface Azimuth (°)", value=15.0, format="%.2f")
        latitude = st.number_input("Latitude (°)", value=43.0, format="%.2f")

    submitted = st.form_submit_button("Calculate Angle")

if submitted:
    result = berechne_solar_incidence_exakt(declination, hour_angle, slope_angle, surface_azimuth, latitude)
    st.success(f"**Calculated Incidence Angle:** {result:.4f}°")
