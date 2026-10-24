"""Clear-sky radiation on a horizontal surface (Hottel beam + Liu & Jordan diffuse).

Pure Python (no Streamlit). Method: Duffie & Beckman, Week 3 of the course.
"""
import math

from solar.angles import (
    cos_zenith,
    declination_deg,
    sunrise_sunset,
    zeit_label,
)

GSC = 1367.0  # Solar constant [W/m2]

# Korrekturfaktoren (r0, r1, rk) für Hottels Koeffizienten je Klimazone
CLIMATES = {
    "Standard atmosphere (no correction)": (1.00, 1.00, 1.00),
    "Tropical": (0.95, 0.98, 1.02),
    "Midlatitude summer": (0.97, 0.99, 1.02),
    "Subarctic summer": (0.99, 0.99, 1.01),
    "Midlatitude winter": (1.03, 1.01, 1.00),
}


def extraterrestrial_normal(n):
    """G_on: extraterrestrial radiation normal to the beam on day n [W/m2]."""
    return GSC * (1 + 0.033 * math.cos(math.radians(360.0 * n / 365.0)))


def hottel_coefficients(altitude_km, climate):
    """Hottel's a0, a1, k for a given altitude [km] and climate type."""
    r0, r1, rk = CLIMATES[climate]
    a0 = r0 * (0.4237 - 0.00821 * (6.0 - altitude_km) ** 2)
    a1 = r1 * (0.5055 + 0.00595 * (6.5 - altitude_km) ** 2)
    k = rk * (0.2711 + 0.01858 * (2.5 - altitude_km) ** 2)
    return a0, a1, k


def beam_transmittance(cos_z, altitude_km, climate):
    """Hottel: tau_b = a0 + a1 * exp(-k / cos(theta_z))."""
    a0, a1, k = hottel_coefficients(altitude_km, climate)
    return a0 + a1 * math.exp(-k / cos_z)


def diffuse_transmittance(tau_b):
    """Liu & Jordan: tau_d = 0.271 - 0.294 * tau_b."""
    return 0.271 - 0.294 * tau_b


def berechne_clear_sky_tag(latitude, altitude_km, n, climate):
    """
    Clear-sky Strahlung auf horizontaler Fläche für einen ganzen Tag.
    Hottel (Beam) + Liu & Jordan (Diffuse), stundenweise am Mittelpunkt.
    Erste/letzte Stunde werden auf den hellen Teil gekürzt.
    Gibt (Deklination, Sonnenaufgang, Sonnenuntergang, Zeilen, H_cb, H_cd) zurück.
    """
    dec = declination_deg(n)
    g_on = extraterrestrial_normal(n)
    sunrise, sunset = sunrise_sunset(latitude, dec)

    rows = []
    h_b = h_d = 0.0
    for h in range(math.floor(sunrise), math.ceil(sunset)):
        t0, t1 = max(h, sunrise), min(h + 1, sunset)   # nur heller Teil der Stunde
        if t1 <= t0:
            continue
        t_mid = 0.5 * (t0 + t1)
        omega = 15.0 * (t_mid - 12.0)

        cos_z = cos_zenith(latitude, dec, omega)
        if cos_z <= 0:
            continue

        tau_b = beam_transmittance(cos_z, altitude_km, climate)
        tau_d = diffuse_transmittance(tau_b)
        g_cb = tau_b * g_on * cos_z
        g_cd = tau_d * g_on * cos_z
        dt = (t1 - t0) * 3600.0
        i_cb, i_cd = g_cb * dt / 1e6, g_cd * dt / 1e6
        h_b += i_cb
        h_d += i_cd
        rows.append({
            "Time (solar)": f"{zeit_label(t0)}–{zeit_label(t1)}",
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
