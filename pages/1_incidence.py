import streamlit as st

from solar.angles import berechne_solar_incidence_exakt, hour_angle_from_time, parse_uhrzeit
from ui.location import location_input

st.title("☀️ Solar Incidence Angle Calculator")
st.write("Enter your parameters below and click **Calculate** to find the incidence angle.")

# The two choices below are outside the form, so the match list / time check
# appears immediately while typing.

# --- Latitude: from a place name or typed in manually ---
lat_mode = st.radio("Latitude", ["From place name", "Enter manually"],
                    horizontal=True, key="inc_lat_mode")
if lat_mode == "From place name":
    ort = location_input("inc", show_elevation=False)
    latitude = ort["latitude"] if ort else None
else:
    latitude = st.number_input("Latitude (°)", min_value=-90.0, max_value=90.0,
                               value=43.0, format="%.2f", key="inc_lat_manual")

st.divider()

# --- Hour angle: from solar time or typed in manually ---
ha_mode = st.radio("Hour Angle", ["From solar time", "Enter manually"],
                   horizontal=True, key="inc_ha_mode")
if ha_mode == "From solar time":
    zeit_text = st.text_input("Solar Time (HH:MM)", value="10:30", key="inc_ha_time",
                              help="24-hour solar time, e.g. 4:30 or 21:31 (solar noon = 12:00 → 0°)")
    zeit = parse_uhrzeit(zeit_text)
    if zeit is None:
        hour_angle = None
        st.error("Invalid time! Please use the format H:MM or HH:MM (00:00 – 23:59), e.g. 4:30 or 21:31.")
    else:
        hour_angle = hour_angle_from_time(*zeit)
        st.caption(f"⏰ {zeit[0]:02d}:{zeit[1]:02d} solar time → hour angle {hour_angle:.2f}°")
else:
    hour_angle = st.number_input("Hour Angle (°)", min_value=-180.0, max_value=180.0,
                                 value=-22.5, format="%.2f", key="inc_ha_manual")

with st.form("solar_form"):
    col1, col2 = st.columns(2)

    with col1:
        declination = st.number_input("Declination (°)", value=-14.0, format="%.2f")
        slope_angle = st.number_input("Slope Angle / Tilt (°)", value=45.0, format="%.2f")

    with col2:
        surface_azimuth = st.number_input("Surface Azimuth (°)", value=15.0, format="%.2f")

    submitted = st.form_submit_button("Calculate Angle")

if submitted:
    if latitude is None:
        st.error("Please enter a valid location or switch to manual latitude.")
        st.stop()
    if hour_angle is None:
        st.error("Please enter a valid solar time or switch to manual hour angle.")
        st.stop()
    result = berechne_solar_incidence_exakt(declination, hour_angle, slope_angle, surface_azimuth, latitude)
    st.success(
        f"**Calculated Incidence Angle:** {result:.4f}°  "
        f"(latitude {latitude:.2f}°, hour angle {hour_angle:.2f}°)"
    )
