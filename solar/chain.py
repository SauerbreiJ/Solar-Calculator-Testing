"""The full calculation chain: horizontal radiation -> beam/diffuse -> hourly -> tilted surface.

Pure Python (no Streamlit). Used by the Tilted Surface page and the Full Chain wizard.
"""
from solar.angles import declination_deg, rb_hour_average, sunset_hour_angle
from solar.extraterrestrial import daily_extraterrestrial, hourly_extraterrestrial
from solar.split import collares_pereira_rabl, erbs_daily, erbs_hourly, liu_jordan_rd
from solar import tilted


def hour_from_hourly(latitude, n, hour_start, I, slope, surface_azimuth, rho_g, Id=None,
                     declination=None):
    """
    One hour, starting from the measured hourly total I on the horizontal [MJ/m²].
    If Id is None, the diffuse part is estimated with the Erbs hourly correlation.
    """
    dec = declination_deg(n) if declination is None else declination
    w1, w2 = (hour_start - 12) * 15.0, (hour_start + 1 - 12) * 15.0
    io = hourly_extraterrestrial(latitude, n, w1, w2, dec)
    kt = I / io if io > 0 else None
    if Id is None:
        frac = erbs_hourly(kt) if kt is not None else 1.0
        Id = frac * I
    else:
        frac = Id / I if I > 0 else None
    Ib = I - Id
    rb = rb_hour_average(latitude, dec, w1, w2, slope, surface_azimuth)
    rbv = rb["rb"] or 0.0
    return {"dec": dec, "w1": w1, "w2": w2, "Io": io, "kt": kt, "diff_frac": frac,
            "I": I, "Id": Id, "Ib": Ib, "rb": rb,
            "iso": tilted.isotropic(I, Ib, Id, rbv, slope, rho_g),
            "hdkr": tilted.hdkr(I, Ib, Id, io, rbv, slope, rho_g)}


def day_from_daily(latitude, n, H, slope, surface_azimuth, rho_g, declination=None):
    """
    Whole day from the daily total H on the horizontal [MJ/m²]:
    H -> K_T -> H_d (Erbs daily) -> r_t, r_d for every hour -> I, I_d, I_b -> R_b -> I_T.
    """
    dec = declination_deg(n) if declination is None else declination
    ws = sunset_hour_angle(latitude, dec)
    h0 = daily_extraterrestrial(latitude, n, dec)
    KT = H / h0 if h0 > 0 else None
    frac = erbs_daily(KT, ws) if KT is not None else None
    Hd = frac * H if frac is not None else 0.0
    hours = []
    for start in range(0, 24):
        w1, w2 = (start - 12) * 15.0, (start + 1 - 12) * 15.0
        if w2 <= -ws or w1 >= ws:
            continue
        mid = (start + 0.5 - 12) * 15.0
        rt = collares_pereira_rabl(mid, ws)
        rd = liu_jordan_rd(mid, ws)
        I, Id = rt * H, rd * Hd
        Id = min(Id, I)
        Ib = I - Id
        io = hourly_extraterrestrial(latitude, n, w1, w2, dec)
        rb = rb_hour_average(latitude, dec, w1, w2, slope, surface_azimuth)
        rbv = rb["rb"] or 0.0
        hours.append({"start": start, "mid": mid, "rt": rt, "rd": rd, "I": I, "Id": Id, "Ib": Ib,
                      "Io": io, "rb": rbv,
                      "iso": tilted.isotropic(I, Ib, Id, rbv, slope, rho_g),
                      "hdkr": tilted.hdkr(I, Ib, Id, io, rbv, slope, rho_g)})
    return {"dec": dec, "ws": ws, "H0": h0, "KT": KT, "diff_frac": frac, "H": H, "Hd": Hd,
            "hours": hours,
            "HT_iso": sum(h["iso"]["total"] for h in hours),
            "HT_hdkr": sum(h["hdkr"]["total"] for h in hours)}
