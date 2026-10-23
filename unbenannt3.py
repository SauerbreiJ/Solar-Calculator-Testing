import math
import datetime
import re
import pandas as pd
import requests
import streamlit as st

def berechne_solar_incidence_exakt(declination, hour_angle, slope_angle, surface_azimuth, latitude):
    """
    Berechnet den Sonneneinfallswinkel (Incidence Angle) in Grad.
    Bezugssystem für surface_azimuth: 0° = Süden, -90° = Osten, +90° = Westen.
    """
    d = math.radians(declination)
    w = math.radians(hour_angle)
    b = math.radians(slope_angle)
    g = math.radians(surface_azimuth)
    p = math.radians(latitude)

    cos_theta = (
        math.sin(d) * math.sin(p) * math.cos(b) -
        math.sin(d) * math.cos(p) * math.sin(b) * math.cos(g) +
        math.cos(d) * math.cos(p) * math.cos(b) * math.cos(w) +
        math.cos(d) * math.sin(p) * math.sin(b) * math.cos(g) * math.cos(w) +
        math.cos(d) * math.sin(b) * math.sin(g) * math.sin(w)
    )

    # Numerische Grenzen absichern
    cos_theta = max(-1.0, min(1.0, cos_theta))

    return math.degrees(math.acos(cos_theta))


def _parse_uhrzeit(text):
    """
    Liest eine Uhrzeit wie '4:30', '04:30', '21:31' (auch '4.30' oder nur '4') ein.
    Gibt (Stunde, Minute) zurück oder None, wenn das Format ungültig ist.
    """
    m = re.fullmatch(r"\s*(\d{1,2})(?:[:.](\d{2}))?\s*", text)
    if not m:
        return None
    stunde = int(m.group(1))
    minute = int(m.group(2)) if m.group(2) else 0
    if stunde > 23 or minute > 59:
        return None
    return stunde, minute


# --- Clear-Sky Radiation (Hottel + Liu & Jordan) ---
GSC = 1367.0  # Solar constant [W/m2]

# Korrekturfaktoren (r0, r1, rk) für Hottels Koeffizienten je Klimazone
CLIMATES = {
    "Standard atmosphere (no correction)": (1.00, 1.00, 1.00),
    "Tropical": (0.95, 0.98, 1.02),
    "Midlatitude summer": (0.97, 0.99, 1.02),
    "Subarctic summer": (0.99, 0.99, 1.01),
    "Midlatitude winter": (1.03, 1.01, 1.00),
}


def _zeit_label(t):
    """Dezimalstunden -> 'HH:MM'."""
    minuten = round(t * 60)
    return f"{minuten // 60:02d}:{minuten % 60:02d}"


@st.cache_data(show_spinner=False)
def finde_ort(name):
    """Ortsname -> Liste möglicher Treffer (Open-Meteo Geocoding, inkl. Höhe)."""
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": name, "count": 5, "language": "en", "format": "json"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get("results", [])


def _ort_label(o):
    """Anzeigename eines Treffers: 'Madison, Wisconsin, United States'."""
    teile = [o.get("name", "?"), o.get("admin1"), o.get("country")]
    return ", ".join(t for t in teile if t)


def berechne_clear_sky_tag(latitude, altitude_km, n, climate):
    """
    Clear-sky Strahlung auf horizontaler Fläche für einen ganzen Tag.
    Hottel (Beam) + Liu & Jordan (Diffuse), stundenweise am Mittelpunkt.
    Erste/letzte Stunde werden auf den hellen Teil gekürzt.
    Gibt (Deklination, Sonnenaufgang, Sonnenuntergang, Zeilen, H_cb, H_cd) zurück.
    """
    r0, r1, rk = CLIMATES[climate]
    a0 = r0 * (0.4237 - 0.00821 * (6.0 - altitude_km) ** 2)
    a1 = r1 * (0.5055 + 0.00595 * (6.5 - altitude_km) ** 2)
    k = rk * (0.2711 + 0.01858 * (2.5 - altitude_km) ** 2)

    dec = 23.45 * math.sin(math.radians(360.0 * (284 + n) / 365.0))
    g_on = GSC * (1 + 0.033 * math.cos(math.radians(360.0 * n / 365.0)))

    # Sonnenuntergangs-Stundenwinkel -> Sonnenauf-/untergang in Solarzeit
    x = -math.tan(math.radians(latitude)) * math.tan(math.radians(dec))
    x = max(-1.0, min(1.0, x))
    w_ss = math.degrees(math.acos(x))
    sunrise, sunset = 12 - w_ss / 15.0, 12 + w_ss / 15.0

    rows = []
    h_b = h_d = 0.0
    for h in range(math.floor(sunrise), math.ceil(sunset)):
        t0, t1 = max(h, sunrise), min(h + 1, sunset)   # nur heller Teil der Stunde
        if t1 <= t0:
            continue
        t_mid = 0.5 * (t0 + t1)
        omega = 15.0 * (t_mid - 12.0)

        lat_r, dec_r, om_r = map(math.radians, (latitude, dec, omega))
        cos_z = math.cos(lat_r) * math.cos(dec_r) * math.cos(om_r) + math.sin(lat_r) * math.sin(dec_r)
        if cos_z <= 0:
            continue

        tau_b = a0 + a1 * math.exp(-k / cos_z)
        tau_d = 0.271 - 0.294 * tau_b
        g_cb = tau_b * g_on * cos_z
        g_cd = tau_d * g_on * cos_z
        dt = (t1 - t0) * 3600.0
        i_cb, i_cd = g_cb * dt / 1e6, g_cd * dt / 1e6
        h_b += i_cb
        h_d += i_cd
        rows.append({
            "Time (solar)": f"{_zeit_label(t0)}–{_zeit_label(t1)}",
            "ω (°)": round(omega, 1),
            "cos θz": round(cos_z, 3),
            "τb": round(tau_b, 3),
            "τd": round(tau_d, 3),
            "G_cb (W/m²)": round(g_cb, 1),
            "G_cd (W/m²)": round(g_cd, 1),
            "I_cb (MJ/m²)": round(i_cb, 2),
            "I_cd (MJ/m²)": round(i_cd, 2),
            "I_c (MJ/m²)": round(i_cb + i_cd, 2),
        })
    return dec, sunrise, sunset, rows, h_b, h_d


# --- UI Layout ---
st.title("☀️ Solar & Calendar Tools")
tab1, tab2, tab3 = st.tabs([
    "☀️ Solar Incidence Angle",
    "📅 Day of the Year & Hour Angle",
    "🌤️ Clear-Sky Radiation (Day)",
])
with tab1:
    st.subheader("☀️ Solar Incidence Angle Calculator")
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

# --- TAB 2: Day of the Year Calculator ---
with tab2:
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

    st.divider() # Visual separator inside the tab

    # 2. Hour Angle Calculator Section (Underneath)
    st.subheader("⏰ Hour Angle Calculator")
    st.write("Calculate the hour angle from solar time (Solar Noon = 12:00 -> 0°).")

    solar_time_str = st.text_input("Solar Time (HH:MM)", value="10:30", key="ha_time",
                                   help="24-hour format, e.g. 4:30 or 21:31")
    zeit = _parse_uhrzeit(solar_time_str)

    if zeit is None:
        st.error("Invalid time! Please use the format H:MM or HH:MM (00:00 – 23:59), e.g. 4:30 or 21:31.")
    else:
        solar_hour, solar_minute = zeit
        # Hour angle calculation: (Decimal Time - 12) * 15°
        # (Morning hours are negative, afternoon hours are positive)
        decimal_time = solar_hour + (solar_minute / 60.0)
        calculated_hour_angle = (decimal_time - 12.0) * 15.0

        st.info(f"At **{solar_hour:02d}:{solar_minute:02d}** solar time, the Hour Angle is **{calculated_hour_angle:.2f}°**.")

# --- TAB 3: Clear-Sky Radiation for a whole day ---
with tab3:
    st.subheader("🌤️ Clear-Sky Radiation on a Horizontal Surface (Whole Day)")
    st.write(
        "Hourly clear-sky radiation (Hottel beam + Liu & Jordan diffuse), "
        "summed from sunrise to sunset."
    )

    # Ortssuche liegt außerhalb des Formulars, damit die Trefferliste sofort erscheint
    cs_ort = st.text_input("Location", value="Madison", key="cs_ort",
                           help="City name, e.g. Madison, Istanbul, Berlin")
    ort = None
    if len(cs_ort.strip()) >= 2:
        try:
            treffer = finde_ort(cs_ort.strip())
        except requests.RequestException:
            treffer = []
            st.error("Location lookup failed (no internet connection?).")
        else:
            if not treffer:
                st.warning("Location not found. Try only the city name.")
        if treffer:
            idx = st.selectbox("Select match", range(len(treffer)),
                               format_func=lambda i: _ort_label(treffer[i]),
                               key=f"cs_treffer_{cs_ort.strip().lower()}")
            ort = treffer[idx]
            st.caption(f"📍 Latitude {ort['latitude']:.2f}° · "
                       f"Elevation {ort.get('elevation') or 0:.0f} m")

    with st.form("clear_sky_form"):
        c1, c2 = st.columns(2)
        with c1:
            cs_n = st.number_input("Day of the year n", min_value=1, max_value=365,
                                   value=234, step=1, key="cs_n",
                                   help="Aug 22 = 234. See the Day of the Year tab.")
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
                f"Declination **{dec:.2f}°** · Sunrise **{_zeit_label(sr)}** · "
                f"Sunset **{_zeit_label(ss)}** · Day length **{ss - sr:.2f} h** (solar time)"
            )
            m1, m2, m3 = st.columns(3)
            m1.metric("Beam H_cb", f"{h_b:.2f} MJ/m²")
            m2.metric("Diffuse H_cd", f"{h_d:.2f} MJ/m²", f"{100 * h_d / h_c:.1f} % of total", delta_color="off")
            m3.metric("Total H_c", f"{h_c:.2f} MJ/m²", f"{h_c / 3.6:.2f} kWh/m²", delta_color="off")

            df = pd.DataFrame(rows)
            st.dataframe(df, hide_index=True)
            st.bar_chart(df.set_index("Time (solar)")[["I_cb (MJ/m²)", "I_cd (MJ/m²)"]])
