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


# ---------------------------------------------------------------------------
# Additions: Spencer declination, solar time, solar azimuth, Rb
# ---------------------------------------------------------------------------

def day_of_year(day, month):
    """Day number n (1 Jan = 1) for a non-leap year, as in the lecture."""
    days_before = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
    return days_before[month - 1] + day


# Recommended "mean day" of each month (Duffie & Beckman Table 1.6.1)
MEAN_DAY_OF_MONTH = (17, 47, 75, 105, 135, 162, 198, 228, 258, 288, 318, 344)


def declination_spencer_deg(n):
    """Declination with the more accurate Spencer (1971) equation [°]."""
    b = math.radians((n - 1) * 360.0 / 365.0)
    rad = (0.006918 - 0.399912 * math.cos(b) + 0.070257 * math.sin(b)
           - 0.006758 * math.cos(2 * b) + 0.000907 * math.sin(2 * b)
           - 0.002697 * math.cos(3 * b) + 0.00148 * math.sin(3 * b))
    return math.degrees(rad)


def equation_of_time_min(n):
    """Equation of time E [minutes]."""
    b = math.radians((n - 1) * 360.0 / 365.0)
    return 229.2 * (0.000075 + 0.001868 * math.cos(b) - 0.032077 * math.sin(b)
                    - 0.014615 * math.cos(2 * b) - 0.04089 * math.sin(2 * b))


def solar_time_correction_min(n, longitude, std_meridian):
    """
    Solar time - standard time [minutes].
    Longitudes EAST positive (Madison = -89.4°, Istanbul = +29.0°).
    Same as the lecture formula 4(L_st - L_loc) + E with west-positive longitudes.
    """
    return 4.0 * (longitude - std_meridian) + equation_of_time_min(n)


def clock_to_solar_time(clock_hours, n, longitude, std_meridian, dst=False):
    """Clock time (decimal h) -> solar time (decimal h). With DST, 1 h is subtracted first."""
    standard = clock_hours - (1.0 if dst else 0.0)
    return standard + solar_time_correction_min(n, longitude, std_meridian) / 60.0


def solar_azimuth(latitude, declination, hour_angle):
    """Solar azimuth γs [°]: 0 = south, east negative, west positive."""
    cz = cos_zenith(latitude, declination, hour_angle)
    cz = max(-1.0, min(1.0, cz))
    sz = math.sqrt(1.0 - cz * cz)
    if sz < 1e-9:
        return 0.0
    p, d = math.radians(latitude), math.radians(declination)
    if abs(math.cos(p)) < 1e-9:
        return 0.0
    x = (cz * math.sin(p) - math.sin(d)) / (sz * math.cos(p))
    x = max(-1.0, min(1.0, x))
    g = math.degrees(math.acos(x))
    return -g if hour_angle < 0 else g


def cos_incidence(latitude, declination, hour_angle, slope, surface_azimuth):
    """cos θ on a tilted surface (not clamped, may be negative = sun behind the surface)."""
    d, w, b, g, p = map(math.radians, (declination, hour_angle, slope, surface_azimuth, latitude))
    return (math.sin(d) * math.sin(p) * math.cos(b)
            - math.sin(d) * math.cos(p) * math.sin(b) * math.cos(g)
            + math.cos(d) * math.cos(p) * math.cos(b) * math.cos(w)
            + math.cos(d) * math.sin(p) * math.sin(b) * math.cos(g) * math.cos(w)
            + math.cos(d) * math.sin(b) * math.sin(g) * math.sin(w))


def rb_instant(latitude, declination, hour_angle, slope, surface_azimuth):
    """Rb = cos θ / cos θz at one moment. Returns None when the sun is below the horizon."""
    cz = cos_zenith(latitude, declination, hour_angle)
    if cz <= 0:
        return None
    return max(0.0, cos_incidence(latitude, declination, hour_angle, slope, surface_azimuth)) / cz


def rb_hour_average(latitude, declination, w1, w2, slope, surface_azimuth):
    """
    Hour-averaged Rb = a / b (Duffie & Beckman eq. 2.14.6) between hour angles w1 < w2.
    The limits are clipped to sunrise/sunset. If the sun is behind the surface for part
    of the period, the integral of max(cos θ, 0) is taken numerically instead.
    Returns dict with the used limits, a, b, Rb (Rb None if the sun is down).
    """
    ws = sunset_hour_angle(latitude, declination)
    lo, hi = max(w1, -ws), min(w2, ws)
    out = {"w1": lo, "w2": hi, "ws": ws, "a": 0.0, "b": 0.0, "rb": None, "numeric": False}
    if hi <= lo:
        return out
    d, b_, g, p = map(math.radians, (declination, slope, surface_azimuth, latitude))
    r1, r2 = math.radians(lo), math.radians(hi)
    a = ((math.sin(d) * math.sin(p) * math.cos(b_)
          - math.sin(d) * math.cos(p) * math.sin(b_) * math.cos(g)) * (r2 - r1)
         + (math.cos(d) * math.cos(p) * math.cos(b_)
            + math.cos(d) * math.sin(p) * math.sin(b_) * math.cos(g)) * (math.sin(r2) - math.sin(r1))
         - (math.cos(d) * math.sin(b_) * math.sin(g)) * (math.cos(r2) - math.cos(r1)))
    b = (math.cos(p) * math.cos(d) * (math.sin(r2) - math.sin(r1))
         + math.sin(p) * math.sin(d) * (r2 - r1))
    # Is the sun behind the surface somewhere in the interval?
    steps = 400
    vals = [cos_incidence(latitude, declination, lo + (hi - lo) * i / steps, slope, surface_azimuth)
            for i in range(steps + 1)]
    if min(vals) < 0:
        h = math.radians(hi - lo) / steps
        pos = [max(0.0, v) for v in vals]
        a = h * (sum(pos) - 0.5 * (pos[0] + pos[-1]))   # trapezoidal rule
        out["numeric"] = True
    out.update(a=a, b=b, rb=(a / b if b > 0 else None))
    return out


def rb_noon_south(latitude, declination, slope):
    """Rb at solar noon for a surface facing the equator (γ = 0° north / 180° south hemisphere)."""
    if latitude >= 0:
        return math.cos(math.radians(abs(latitude - declination - slope))) / \
            math.cos(math.radians(abs(latitude - declination)))
    return math.cos(math.radians(abs(-latitude + declination - slope))) / \
        math.cos(math.radians(abs(-latitude + declination)))
