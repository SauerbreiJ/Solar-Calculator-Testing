import datetime

import streamlit as st

from solar.angles import hour_angle_from_time, parse_uhrzeit

st.title("📅 Day of the Year & Hour Angle")

# 1. Day of the Year Section
st.subheader("📅 Day of the Year Calculator")
st.write("Enter the day and month to get the day of the year.")

col1, col2 = st.columns(2)
with col1:
    day = st.number_input("Day", min_value=1, max_value=31, value=13, step=1)
with col2:
    month = st.number_input("Month", min_value=1, max_value=12, value=5, step=1)

current_year = datetime.date.today().year

try:
    calc_date = datetime.date(current_year, month, day)
    day_of_year = calc_date.timetuple().tm_yday
    suffix = "th" if 11 <= day_of_year % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day_of_year % 10, "th")
    st.info(f"**{day:02d}.{month:02d}.** is the **{day_of_year}{suffix}** day of the year.")
except ValueError:
    st.error("Invalid date! Please check the day and month.")

st.divider()  # Visual separator

# 2. Hour Angle Calculator Section (Underneath)
st.subheader("⏰ Hour Angle Calculator")
st.write("Calculate the hour angle from solar time (Solar Noon = 12:00 -> 0°).")

solar_time_str = st.text_input("Solar Time (HH:MM)", value="10:30", key="ha_time",
                               help="24-hour format, e.g. 4:30 or 21:31")
zeit = parse_uhrzeit(solar_time_str)

if zeit is None:
    st.error("Invalid time! Please use the format H:MM or HH:MM (00:00 – 23:59), e.g. 4:30 or 21:31.")
else:
    solar_hour, solar_minute = zeit
    # (Morning hours are negative, afternoon hours are positive)
    calculated_hour_angle = hour_angle_from_time(solar_hour, solar_minute)
    st.info(f"At **{solar_hour:02d}:{solar_minute:02d}** solar time, the Hour Angle is **{calculated_hour_angle:.2f}°**.")
