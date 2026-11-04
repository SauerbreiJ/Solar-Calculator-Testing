"""Checks of the new modules against the worked examples of the lecture (ESE 5509, Weeks 2-4)
and Duffie & Beckman. Run from the project root:  python -m pytest tests -q
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solar.angles import (
    clock_to_solar_time, day_of_year, declination_deg, declination_spencer_deg,
    rb_hour_average, rb_instant, rb_noon_south, solar_azimuth, sunset_hour_angle,
)
from solar.chain import day_from_daily, hour_from_hourly
from solar.extraterrestrial import daily_extraterrestrial, hourly_extraterrestrial, spectral_split
from solar.split import collares_pereira_rabl, erbs_daily, erbs_hourly, erbs_monthly, liu_jordan_rd
from solar.sunshine import angstrom_prescott, monthly_table


def close(a, b, tol):
    return abs(a - b) <= tol


# ---------------- Week 2 ----------------
def test_week2_example1_spectral_split():
    s = spectral_split()
    assert close(s["Ultraviolet"][1], 87.5, 0.5)
    assert close(s["Visible"][1], 656.2, 0.5)
    assert close(s["Infrared"][1], 623.4, 0.5)


def test_week2_example2_solar_time():
    # Madison (89.4° W, central time 90° W), Feb 3, 10:30 -> 10:19 solar time
    n = day_of_year(3, 2)
    st = clock_to_solar_time(10.5, n, -89.4, -90.0)
    assert close(st * 60, 10 * 60 + 19, 0.5), st


def test_week2_example5_azimuth():
    # 40° N, June 16, 2 h after noon: azimuth 65.67° (west positive)
    assert close(solar_azimuth(40.0, 23.35, 30.0), 65.67, 0.1)
    assert close(solar_azimuth(40.0, 23.35, -30.0), -65.67, 0.1)


def test_week2_example7_rb():
    assert close(rb_instant(40.0, -13.0, -37.5, 30.0, 0.0), 1.61, 0.01)


def test_week2_example8_daily_extraterrestrial():
    assert close(daily_extraterrestrial(43.0, day_of_year(15, 4)), 33.8, 0.05)


def test_week2_example9_hourly_extraterrestrial():
    assert close(hourly_extraterrestrial(43.0, day_of_year(15, 4), -30.0, -15.0), 3.79, 0.01)


def test_spencer_close_to_cooper():
    for n in (1, 80, 172, 266, 355):
        assert abs(declination_spencer_deg(n) - declination_deg(n)) < 1.5


def test_rb_noon_matches_general_formula():
    assert close(rb_noon_south(40.0, -13.0, 30.0), rb_instant(40.0, -13.0, 0.0, 30.0, 0.0), 1e-9)


# ---------------- Week 3 ----------------
def test_week3_angstrom_prescott():
    h, kt = angstrom_prescott(20.0, 6.0, 12.0, 0.25, 0.5)
    assert close(kt, 0.5, 1e-12) and close(h, 10.0, 1e-12)
    rows = monthly_table(43.0, [5.0] * 12, 0.30, 0.34)
    assert len(rows) == 12 and all(r["H"] > 0 for r in rows)


def test_week3_example4_erbs_daily_st_louis():
    # St. Louis 38.6° N, Sept 3, H = 23.0 MJ/m² -> K_T ≈ 0.70, H_d/H ≈ 0.24-0.25
    n = day_of_year(3, 9)
    dec = declination_deg(n)
    ws = sunset_hour_angle(38.6, dec)
    KT = 23.0 / daily_extraterrestrial(38.6, n)
    assert close(KT, 0.70, 0.015)
    assert close(erbs_daily(KT, ws), 0.25, 0.015)


def test_week3_example5_rt_melbourne():
    # Melbourne (-37.8°), January (mean day 17), hour 8-9 (ω = -52.5°) -> r_t ≈ 0.075
    ws = sunset_hour_angle(-37.8, declination_deg(17))
    assert close(collares_pereira_rabl(-52.5, ws), 0.075, 0.003)


def test_week3_example6_hourly_from_daily_madison():
    # Madison, Aug 23, H = 31.4 MJ/m², 13-14 h -> r_t ≈ 0.118, I ≈ 3.7 MJ/m²
    ws = sunset_hour_angle(43.0, declination_deg(day_of_year(23, 8)))
    rt = collares_pereira_rabl(22.5, ws)
    assert close(rt, 0.118, 0.002)
    assert close(rt * 31.4, 3.7, 0.05)


def test_erbs_branches_continuous_enough():
    assert close(erbs_hourly(0.22), 1 - 0.09 * 0.22, 1e-12)
    assert 0.1 < erbs_hourly(0.8) < 0.25
    assert close(erbs_monthly(0.5, 90.0), 1.311 - 3.022 * .5 + 3.427 * .25 - 1.821 * .125, 1e-12)


def test_rt_rd_sum_to_about_one():
    ws = sunset_hour_angle(43.0, declination_deg(200))
    s_t = sum(collares_pereira_rabl((h + 0.5 - 12) * 15, ws) for h in range(24))
    s_d = sum(liu_jordan_rd((h + 0.5 - 12) * 15, ws) for h in range(24))
    assert close(s_t, 1.0, 0.03) and close(s_d, 1.0, 0.03)


# ---------------- Week 4 ----------------
def test_week4_example1_rb_average_vs_instant():
    # March 4, 45° N, slope 60° south: Rb at 6:30 is huge, the hour average is much smaller
    dec = declination_deg(day_of_year(4, 3))
    inst = rb_instant(45.0, dec, -82.5, 60.0, 0.0)
    avg = rb_hour_average(45.0, dec, -90.0, -75.0, 60.0, 0.0)
    assert inst > 20
    assert close(avg["rb"], 4.61, 0.05)
    assert close(avg["w1"], -sunset_hour_angle(45.0, dec), 1e-9)


def test_week4_example2_isotropic():
    # 40° N, Feb 20, 9-10 h, slope 60° south, I = 1.04 MJ/m², ρg = 0.6 -> I_T ≈ 1.17 MJ/m²
    r = hour_from_hourly(40.0, day_of_year(20, 2), 9, 1.04, 60.0, 0.0, 0.6)
    assert close(r["Io"], 2.34, 0.01)
    assert close(r["kt"], 0.445, 0.005)
    assert close(r["rb"]["rb"], 1.71, 0.01)
    assert close(r["iso"]["total"], 1.17, 0.01)


def test_week4_example3_hdkr():
    r = hour_from_hourly(40.0, day_of_year(20, 2), 9, 1.04, 60.0, 0.0, 0.6)
    assert close(r["hdkr"]["Ai"], 0.104, 0.002)
    assert close(r["hdkr"]["total"], 1.28, 0.01)


def test_full_day_chain_energy_balance():
    d = day_from_daily(43.0, day_of_year(23, 8), 31.4, 0.0, 0.0, 0.2)
    # horizontal surface (β = 0): tilted total must equal the horizontal hourly sum
    total_h = sum(h["I"] for h in d["hours"])
    assert close(d["HT_iso"], total_h, 1e-6)
    assert close(total_h, 31.4, 1.0)
