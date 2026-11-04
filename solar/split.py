"""Beam / diffuse split (Erbs et al.) and daily -> hourly (Collares-Pereira & Rabl, Liu & Jordan).

Week 3 of the course. Pure Python (no Streamlit). Angles in degrees, energy in MJ/m².
"""
import math


def erbs_hourly(kt):
    """Hourly diffuse fraction I_d / I from the hourly clearness index k_T."""
    if kt <= 0.22:
        return 1.0 - 0.09 * kt
    if kt <= 0.80:
        return 0.9511 - 0.1604 * kt + 4.388 * kt**2 - 16.638 * kt**3 + 12.336 * kt**4
    return 0.165


def erbs_hourly_branch(kt):
    return "k_T ≤ 0.22" if kt <= 0.22 else ("0.22 < k_T ≤ 0.80" if kt <= 0.80 else "k_T > 0.80")


def erbs_daily(KT, ws):
    """Daily diffuse fraction H_d / H from the daily clearness index K_T and sunset hour angle ω_s."""
    if ws <= 81.4:
        if KT < 0.715:
            return 1.0 - 0.2727 * KT + 2.4495 * KT**2 - 11.9514 * KT**3 + 9.3879 * KT**4
        return 0.143
    if KT < 0.722:
        return 1.0 + 0.2832 * KT - 2.5557 * KT**2 + 0.8448 * KT**3
    return 0.175


def erbs_daily_branch(KT, ws):
    if ws <= 81.4:
        return "ω_s ≤ 81.4° and " + ("K_T < 0.715" if KT < 0.715 else "K_T ≥ 0.715")
    return "ω_s > 81.4° and " + ("K_T < 0.722" if KT < 0.722 else "K_T ≥ 0.722")


def erbs_monthly(KT_bar, ws):
    """Monthly average diffuse fraction H̄_d / H̄ (valid for 0.3 ≤ K̄_T ≤ 0.8)."""
    if ws <= 81.4:
        return 1.391 - 3.560 * KT_bar + 4.189 * KT_bar**2 - 2.137 * KT_bar**3
    return 1.311 - 3.022 * KT_bar + 3.427 * KT_bar**2 - 1.821 * KT_bar**3


def collares_pereira_rabl(omega, ws):
    """r_t = I / H: fraction of the daily TOTAL radiation in the hour centred at ω."""
    if abs(omega) >= ws:
        return 0.0
    w, s = math.radians(omega), math.radians(ws)
    a = 0.409 + 0.5016 * math.sin(math.radians(ws - 60))
    b = 0.6609 - 0.4767 * math.sin(math.radians(ws - 60))
    return (math.pi / 24 * (a + b * math.cos(w))
            * (math.cos(w) - math.cos(s)) / (math.sin(s) - s * math.cos(s)))


def crp_coefficients(ws):
    a = 0.409 + 0.5016 * math.sin(math.radians(ws - 60))
    b = 0.6609 - 0.4767 * math.sin(math.radians(ws - 60))
    return a, b


def liu_jordan_rd(omega, ws):
    """r_d = I_d / H_d: fraction of the daily DIFFUSE radiation in the hour centred at ω."""
    if abs(omega) >= ws:
        return 0.0
    w, s = math.radians(omega), math.radians(ws)
    return math.pi / 24 * (math.cos(w) - math.cos(s)) / (math.sin(s) - s * math.cos(s))
