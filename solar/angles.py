"""Solar geometry: declination, hour angle, zenith, incidence angle, sunrise/sunset.

Pure Python (no Streamlit). All angles in degrees unless noted.
"""
import math
import re


def declination_deg(n):
    """Declination for day of the year n (Cooper equation)."""
    return 23.45 * math.sin(math.radians(360.0 * (284 + n) / 365.0))


def parse_uhrzeit(text):
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


def hour_angle_from_time(hour, minute=0):
    """Hour angle from solar time: (decimal time - 12) * 15°. Morning negative."""
    return (hour + minute / 60.0 - 12.0) * 15.0


def zeit_label(t):
    """Dezimalstunden -> 'HH:MM'."""
    minuten = round(t * 60)
    return f"{minuten // 60:02d}:{minuten % 60:02d}"


def cos_zenith(latitude, declination, hour_angle):
    """cos of the zenith angle (angle of incidence on a horizontal surface)."""
    p, d, w = map(math.radians, (latitude, declination, hour_angle))
    return math.cos(p) * math.cos(d) * math.cos(w) + math.sin(p) * math.sin(d)


def sunset_hour_angle(latitude, declination):
    """Sunset hour angle ω_ss (°). Clamped for polar day / polar night."""
    x = -math.tan(math.radians(latitude)) * math.tan(math.radians(declination))
    x = max(-1.0, min(1.0, x))
    return math.degrees(math.acos(x))


def sunrise_sunset(latitude, declination):
    """Sunrise and sunset in solar time (decimal hours)."""
    w_ss = sunset_hour_angle(latitude, declination)
    return 12 - w_ss / 15.0, 12 + w_ss / 15.0


def day_length(latitude, declination):
    """Day length in hours: N = (2/15) * ω_ss."""
    return 2.0 * sunset_hour_angle(latitude, declination) / 15.0


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
