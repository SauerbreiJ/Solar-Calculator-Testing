"""Radiation on a tilted surface: isotropic sky (Liu & Jordan) and HDKR. Week 4 of the course.

Pure Python (no Streamlit). Works with hourly energies [MJ/m²] (or irradiances, same units in and out).
"""
import math


def view_factors(slope):
    """(sky, ground) view factors of a surface with slope β."""
    c = math.cos(math.radians(slope))
    return (1 + c) / 2, (1 - c) / 2


def isotropic(I, Ib, Id, rb, slope, rho_g):
    """I_T = I_b R_b + I_d (1+cosβ)/2 + I ρ_g (1−cosβ)/2. Returns dict of components."""
    f_sky, f_gnd = view_factors(slope)
    beam = Ib * rb
    diffuse = Id * f_sky
    ground = I * rho_g * f_gnd
    total = beam + diffuse + ground
    return {"beam": beam, "diffuse": diffuse, "ground": ground, "total": total,
            "R": total / I if I > 0 else None, "f_sky": f_sky, "f_gnd": f_gnd}


def hdkr(I, Ib, Id, Io, rb, slope, rho_g):
    """
    Hay-Davies-Klucher-Reindl model.
    A_i = I_b / I_o (anisotropy index), f = sqrt(I_b / I) (horizon brightening).
    I_T = (I_b + I_d A_i) R_b + I_d (1−A_i) (1+cosβ)/2 [1 + f sin³(β/2)] + I ρ_g (1−cosβ)/2
    """
    f_sky, f_gnd = view_factors(slope)
    ai = Ib / Io if Io > 0 else 0.0
    f = math.sqrt(Ib / I) if I > 0 else 0.0
    horizon = 1 + f * math.sin(math.radians(slope) / 2) ** 3
    beam = Ib * rb
    circumsolar = Id * ai * rb
    iso_diffuse = Id * (1 - ai) * f_sky * horizon
    ground = I * rho_g * f_gnd
    total = beam + circumsolar + iso_diffuse + ground
    return {"beam": beam, "circumsolar": circumsolar, "diffuse": iso_diffuse, "ground": ground,
            "total": total, "R": total / I if I > 0 else None, "Ai": ai, "f": f,
            "horizon": horizon, "f_sky": f_sky, "f_gnd": f_gnd}
