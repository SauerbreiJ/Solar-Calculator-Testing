"""Small reusable Streamlit pieces: time input, step-by-step display, number formatting."""
import streamlit as st

from solar.angles import clock_to_solar_time, parse_uhrzeit, solar_time_correction_min, zeit_label

# Fixed colour per radiation component (categorical slots, same entity = same colour everywhere)
COLORS = {"Beam": "#2a78d6", "Diffuse": "#eb6834", "Ground-reflected": "#1baf7a", "Circumsolar": "#eda100"}


def fmt(x, d=3):
    return "–" if x is None else f"{x:.{d}f}"


def init(key, value):
    """Default for a widget key (so lecture examples can overwrite it later)."""
    st.session_state.setdefault(key, value)


def time_input(prefix, site, default="10:30", allow_clock=True):
    """
    Time field with a solar/clock toggle. Returns (solar time in decimal hours or None, steps).
    Clock time is converted with the sidebar longitude and standard meridian.
    """
    init(f"{prefix}_tmode", "Solar time")
    init(f"{prefix}_time", default)
    init(f"{prefix}_dst", False)
    if allow_clock:
        st.radio("Time is given as", ["Solar time", "Clock time"], key=f"{prefix}_tmode", horizontal=True)
    c1, c2 = st.columns([2, 1])
    c1.text_input("Time (HH:MM)", key=f"{prefix}_time", help="24-hour format, e.g. 9:30 or 14:00")
    is_clock = allow_clock and st.session_state[f"{prefix}_tmode"] == "Clock time"
    if is_clock:
        c2.checkbox("Daylight saving", key=f"{prefix}_dst", help="Subtracts 1 h before converting")
    t = parse_uhrzeit(st.session_state[f"{prefix}_time"])
    if t is None:
        st.error("Invalid time – use H:MM or HH:MM (00:00–23:59).")
        return None, []
    hours = t[0] + t[1] / 60.0
    if not is_clock:
        return hours, []
    corr = solar_time_correction_min(site["n"], site["lon"], site["lst"])
    from solar.angles import equation_of_time_min
    e = equation_of_time_min(site["n"])
    solar = clock_to_solar_time(hours, site["n"], site["lon"], site["lst"], st.session_state[f"{prefix}_dst"])
    st.caption(f"🕐 {zeit_label(hours)} clock time → **{zeit_label(solar % 24)} solar time** "
               f"(correction {corr:+.1f} min)")
    steps = [
        ("Equation of time", rf"B = \frac{{(n-1)\,360}}{{365}},\quad E = {e:.2f}\ \text{{min}}"),
        ("Solar time (longitudes east positive)",
         rf"t_{{solar}} = t_{{std}} + 4(L_{{loc}} - L_{{st}}) + E = t_{{std}} + 4({site['lon']:.2f} - ({site['lst']:.0f})) "
         rf"+ ({e:.2f}) = t_{{std}} {corr:+.1f}\ \text{{min}}"),
    ]
    return solar, steps


def show_steps(steps, expanded=False, title="📝 Show steps"):
    """steps: list of (description, latex). Rendered in an expander."""
    if not steps:
        return
    with st.expander(title, expanded=expanded):
        for i, (text, latex) in enumerate(steps, 1):
            st.markdown(f"**{i}. {text}**")
            st.latex(latex)


def hour_select(key, default=9, label="Hour (solar time)"):
    """Select an hour like '09:00–10:00'. Returns the start hour."""
    init(key, default)
    return st.selectbox(label, list(range(24)), key=key,
                        format_func=lambda h: f"{h:02d}:00–{h + 1:02d}:00")
