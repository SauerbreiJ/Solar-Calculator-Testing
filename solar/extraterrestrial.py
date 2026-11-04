"""Extraterrestrial radiation: G_on, H_o (day), I_o (hour). Week 2 of the course.

Pure Python (no Streamlit).
"""
import math

from solar.angles import declination_deg, sunset_hour_angle

GSC = 1367.0  # Solar constant [W/m²]


def extraterrestrial_normal(n):
    """G_on: extraterrestrial radiation normal to the beam on day n [W/m²]."""
    return GSC * (1 + 0.033 * math.cos(math.radians(360.0 * n / 365.0)))


def daily_extraterrestrial(latitude, n, declination=None):
    """H_o: daily extraterrestrial radiation on a horizontal surface [MJ/m²]."""
    dec = declination_deg(n) if declination is None else declination
    ws = sunset_hour_angle(latitude, dec)
    p, d = math.radians(latitude), math.radians(dec)
    h = (24 * 3600 * GSC / math.pi * (1 + 0.033 * math.cos(math.radians(360.0 * n / 365.0)))
         * (math.cos(p) * math.cos(d) * math.sin(math.radians(ws))
            + math.pi * ws / 180.0 * math.sin(p) * math.sin(d)))
    return max(0.0, h) / 1e6


def hourly_extraterrestrial(latitude, n, w1, w2, declination=None):
    """
    I_o: extraterrestrial radiation on a horizontal surface between hour angles w1 and w2 [MJ/m²].
    The limits are clipped to sunrise / sunset.
    """
    dec = declination_deg(n) if declination is None else declination
    ws = sunset_hour_angle(latitude, dec)
    lo, hi = max(w1, -ws), min(w2, ws)
    if hi <= lo:
        return 0.0
    p, d = math.radians(latitude), math.radians(dec)
    i = (12 * 3600 * GSC / math.pi * (1 + 0.033 * math.cos(math.radians(360.0 * n / 365.0)))
         * (math.cos(p) * math.cos(d) * (math.sin(math.radians(hi)) - math.sin(math.radians(lo)))
            + math.pi * (hi - lo) / 180.0 * math.sin(p) * math.sin(d)))
    return max(0.0, i) / 1e6


# Fraction of extraterrestrial energy below wavelength λ (WRC spectrum, D&B Table 1.3.1, selected)
# Used for the UV / visible / IR split of Week 2, Example 1.
F0_LAMBDA = {0.38: 0.064, 0.78: 0.544}


def spectral_split():
    """UV (<0.38 µm), visible (0.38–0.78 µm), IR (>0.78 µm): (fraction, W/m²) each."""
    uv = F0_LAMBDA[0.38]
    vis = F0_LAMBDA[0.78] - F0_LAMBDA[0.38]
    ir = 1 - F0_LAMBDA[0.78]
    return {name: (f, f * GSC) for name, f in (("Ultraviolet", uv), ("Visible", vis), ("Infrared", ir))}
