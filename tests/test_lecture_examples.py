"""Checks against the worked examples of the lecture (ESE 5509, Weeks 2-3).

Run from the project root:  python -m pytest tests -q
(or without pytest:        python tests/test_lecture_examples.py)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solar.angles import (
    berechne_solar_incidence_exakt,
    cos_zenith,
    day_length,
    declination_deg,
    hour_angle_from_time,
    parse_uhrzeit,
)
from solar.clear_sky import (
    beam_transmittance,
    berechne_clear_sky_tag,
    diffuse_transmittance,
    extraterrestrial_normal,
)


def close(a, b, tol):
    return abs(a - b) <= tol


def test_week2_example3_incidence_angle():
    # Madison, 10:30 solar time, Feb 13: slope 45°, 15° west of south -> theta = 35°
    theta = berechne_solar_incidence_exakt(-14.0, -22.5, 45.0, 15.0, 43.0)
    assert close(theta, 35.0, 0.3), theta


def test_week2_example4_zenith_angles():
    # lat 43°: a) 9:30 on Feb 13 -> 66.5°, b) 18:30 on July 1 -> 79.6°
    za = math.degrees(math.acos(cos_zenith(43.0, -14.0, -37.5)))
    zb = math.degrees(math.acos(cos_zenith(43.0, 23.1, 97.5)))
    assert close(za, 66.5, 0.2), za
    assert close(zb, 79.6, 0.2), zb


def test_week2_example5_day_length():
    # 40°N, June 16 (n = 167, delta = 23.35°) -> 14.83 h
    assert close(day_length(40.0, 23.35), 14.83, 0.01)


def test_week2_example6_rb():
    # Rb = cos(theta) / cos(theta_z) = 1.67 for the surface of Example 3
    theta = berechne_solar_incidence_exakt(-14.0, -22.5, 45.0, 15.0, 43.0)
    rb = math.cos(math.radians(theta)) / cos_zenith(43.0, -14.0, -22.5)
    assert close(rb, 1.67, 0.02), rb


def test_week3_example2_beam_radiation():
    # Madison (270 m), Aug 22 (n = 234), 11:30 -> beam on horizontal = 702 W/m2.
    # Lecture uses the standard atmosphere with Madison's midlatitude-summer correction.
    n, lat, alt = 234, 43.0, 0.270
    dec = declination_deg(n)
    cz = cos_zenith(lat, dec, hour_angle_from_time(11, 30))
    tau_b = beam_transmittance(cz, alt, "Midlatitude summer")
    g_cb = tau_b * extraterrestrial_normal(n) * cz
    assert close(g_cb, 702.0, 3.0), g_cb


def test_week3_example3_clear_day_total():
    # Whole clear day at Madison on Aug 22: ~22.85 MJ/m2, diffuse share 10-20 %
    _, sr, ss, rows, h_b, h_d = berechne_clear_sky_tag(43.0, 0.270, 234, "Midlatitude summer")
    assert close(ss - sr, 13.45, 0.05)
    assert close(h_b + h_d, 22.85, 0.1), h_b + h_d
    assert 0.10 < h_d / (h_b + h_d) < 0.20


def test_diffuse_transmittance_formula():
    assert close(diffuse_transmittance(0.62), 0.271 - 0.294 * 0.62, 1e-12)


def test_time_parser_and_hour_angle():
    assert parse_uhrzeit("4:30") == (4, 30)
    assert parse_uhrzeit("21.31") == (21, 31)
    assert parse_uhrzeit("4") == (4, 0)
    for bad in ("24:00", "7:75", "abc", ""):
        assert parse_uhrzeit(bad) is None
    assert hour_angle_from_time(4, 30) == -112.5
    assert hour_angle_from_time(21, 31) == 142.75


def test_polar_night_has_no_rows():
    assert berechne_clear_sky_tag(80.0, 0.0, 355, "Standard atmosphere (no correction)")[3] == []


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok  ", t.__name__)
