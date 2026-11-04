"""Average radiation from sunshine hours (Angström-Prescott). Week 3 of the course.

Pure Python (no Streamlit).
"""
from solar.angles import MEAN_DAY_OF_MONTH, day_length, declination_deg
from solar.extraterrestrial import daily_extraterrestrial

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# Angström-Prescott coefficients (a, b). Free inputs in the app; these are starting points.
PRESETS = {
    "Generic (Page): a = 0.25, b = 0.50": (0.25, 0.50),
    "Madison, WI (lecture example): a = 0.30, b = 0.34": (0.30, 0.34),
    "Custom": None,
}


def angstrom_prescott(h0_bar, n_bar, N_bar, a, b):
    """H̄ = H̄o (a + b n̄/N̄). Returns (H̄, K̄T)."""
    kt = a + b * n_bar / N_bar
    return h0_bar * kt, kt


def monthly_table(latitude, sunshine_hours, a, b):
    """One row per month (mean day of month) from 12 average daily sunshine hours."""
    rows = []
    for i, n_bar in enumerate(sunshine_hours):
        n = MEAN_DAY_OF_MONTH[i]
        dec = declination_deg(n)
        N = day_length(latitude, dec)
        h0 = daily_extraterrestrial(latitude, n)
        if n_bar is None or N <= 0:
            h, kt = None, None
        else:
            h, kt = angstrom_prescott(h0, n_bar, N, a, b)
        rows.append({"month": MONTHS[i], "n": n, "dec": dec, "N": N, "sun": n_bar,
                     "ratio": (n_bar / N if (n_bar is not None and N > 0) else None),
                     "H0": h0, "KT": kt, "H": h})
    return rows
