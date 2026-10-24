import streamlit as st

from ui import diagrams

st.title("📖 Introduction: Solar Angles, Variables and Terms")
st.write(
    "This page explains the symbols used in the calculators. "
    "Angles are in degrees (°), irradiance in W/m², and energy per area in MJ/m². "
    "Open a section to read it."
)

# ---------------------------------------------------------------- 1
with st.expander("1. Where the sunlight comes from", expanded=True):
    st.markdown(
        """
- **Solar constant G_sc = 1367 W/m²** is the radiation arriving *outside* the atmosphere on a surface
  facing the sun, at mean Earth–sun distance. It is the value adopted by the World Radiation Center.
- **Extraterrestrial radiation** is the radiation we would receive without an atmosphere. It varies by
  about ±3.3 % over the year because Earth's orbit is slightly elliptical.
- **Day number n** counts the days of the year (1 January = 1, 22 August = 234). It is the input for the
  declination and for G_on.
        """
    )

# ---------------------------------------------------------------- 2
with st.expander("2. Types of radiation"):
    st.markdown(
        """
| Term | Meaning |
|---|---|
| **Beam (direct)** | Sunlight that reaches the surface without being scattered |
| **Diffuse** | Sunlight scattered by the atmosphere (clouds, air, dust) |
| **Global / total** | Beam + diffuse. This is what a pyranometer on a horizontal surface measures |
| **Short-wave radiation** | From the sun, wavelengths 0.3–3 μm |
| **Long-wave radiation** | Emitted by the atmosphere, ground and collectors, above 3 μm |
| **Air mass** | How much atmosphere the beam crosses, relative to the sun at the zenith |
        """
    )

# ---------------------------------------------------------------- 3
with st.expander("3. The solar angles"):
    st.markdown(
        """
| Symbol | Name | Meaning | Range and sign |
|---|---|---|---|
| **φ** | Latitude | Position north or south of the equator | −90° to 90°, north positive |
| **δ** | Declination | Angle of the sun's rays north or south of the equator at solar noon. Caused by Earth's 23.45° axis tilt | −23.45° to +23.45° |
| **ω** | Hour angle | How far the sun is east or west of the local meridian. The Earth turns 15° per hour | Morning negative, afternoon positive, 0° at solar noon |
| **θz** | Zenith angle | Angle between the vertical and the sun | 0° (sun overhead) to 90° (horizon) |
| **αs** | Solar altitude | Angle between the horizon and the sun: αs = 90° − θz | 0° to 90° |
| **γs** | Solar azimuth | Compass direction of the sun, measured from south | East of south negative, west positive |
| **β** | Slope (tilt) | Angle between the surface and the horizontal | 0° (flat) to 180° |
| **γ** | Surface azimuth | Direction the surface faces, measured from south | 0° = south, −90° = east, +90° = west |
| **θ** | Angle of incidence | Angle between the sun's rays and the **normal** (the line perpendicular) to the surface | Smaller means more energy on the surface; above 90° the sun is behind the surface |

For a horizontal surface (β = 0°) the angle of incidence equals the zenith angle.
        """
    )

# ---------------------------------------------------------------- 4
with st.expander("4. Diagrams of the angles"):
    st.markdown("**Sun position in the sky**")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(diagrams.zenith_altitude(), unsafe_allow_html=True)
        st.caption("Zenith angle θz and solar altitude αs add up to 90°.")
    with c2:
        st.markdown(diagrams.azimuth_topview(), unsafe_allow_html=True)
        st.caption("Solar azimuth γs is measured from south; west is positive.")

    st.markdown("**Surface and sun**")
    st.markdown(diagrams.slope_incidence(), unsafe_allow_html=True)
    st.caption("Slope β tilts the surface away from the horizontal. The angle of incidence θ is measured "
               "between the sun ray and the normal of the surface, not the surface itself.")

    st.markdown("**Position on Earth and time of day**")
    c3, c4 = st.columns(2)
    with c3:
        st.markdown(diagrams.latitude_declination(), unsafe_allow_html=True)
        st.caption("Latitude φ is the position of the observer. Declination δ is the angle of the sun "
                   "above or below the equatorial plane.")
    with c4:
        st.markdown(diagrams.hour_angle(), unsafe_allow_html=True)
        st.caption("Hour angle ω: the Earth rotates 15° per hour. Afternoon is positive, morning negative.")

# ---------------------------------------------------------------- 5
with st.expander("5. Solar time"):
    st.markdown(
        """
Solar time is based on the sun's position, so it does **not** match the clock. The sun reaches its
highest point at solar noon (12:00 solar time). Two things make solar time differ from the clock:

- your position inside the time zone: the sun takes **4 minutes per degree of longitude**
- a correction for the time of year (the equation of time E, in minutes)

The hour angle follows directly from solar time: **ω = (solar time − 12 h) × 15°/h**.
Examples: 10:30 → −22.5°, 12:00 → 0°, 15:00 → +45°.
        """
    )

# ---------------------------------------------------------------- 6
with st.expander("6. Symbols and subscripts"):
    st.markdown(
        """
**Base symbols**

| Symbol | Meaning | Unit |
|---|---|---|
| **G** | Irradiance: power per area at one moment | W/m² |
| **I** | Insolation for one **hour** | MJ/m² per hour |
| **H** | Insolation for one **day** | MJ/m² per day |

**Subscripts**

| Subscript | Meaning |
|---|---|
| **o** | Outside the atmosphere (extraterrestrial) |
| **b** | Beam |
| **d** | Diffuse |
| **n** | On a plane **normal** to the beam |
| **T** | On a **tilted** plane |
| **c** | Clear-sky |
| *none* | Horizontal surface (if neither n nor T appears) |

Examples: **G_on** is extraterrestrial radiation normal to the beam. **G_cb** is clear-sky beam
radiation on the horizontal. **H_o** is the daily extraterrestrial radiation on a horizontal surface.
        """
    )

# ---------------------------------------------------------------- 7
with st.expander("7. Ratios and coefficients"):
    st.markdown(
        """
| Symbol | Meaning |
|---|---|
| **τ_b** | Beam transmittance of the atmosphere (G_bn / G_on), from Hottel's method |
| **τ_d** | Diffuse transmittance (G_d / G_o), from Liu & Jordan |
| **k_T** | Clearness index: actual radiation divided by extraterrestrial radiation. High = clear day |
| **R_b** | Ratio of beam radiation on a tilted surface to that on a horizontal surface: cos θ / cos θz |
| **r_t** | Ratio of hourly to daily total radiation (Collares-Pereira & Rabl) |
| **TMY** | Typical Meteorological Year: hourly weather data representing a typical year, used in simulations |
        """
    )

# ---------------------------------------------------------------- 8
with st.expander("8. Formulas"):
    st.markdown("**Sun geometry**")
    st.latex(r"\delta = 23.45^\circ \,\sin\!\left(\frac{360\,(284+n)}{365}\right)")
    st.caption("Declination for day number n (Cooper equation).")
    st.latex(r"\omega = 15^\circ/\mathrm{h}\cdot(t_{\mathrm{solar}} - 12\,\mathrm{h})")
    st.caption("Hour angle from solar time.")
    st.latex(r"t_{\mathrm{solar}} - t_{\mathrm{standard}} = 4\,(L_{st} - L_{loc}) + E \quad [\mathrm{min}]")
    st.caption("Solar time from clock time. L_st = standard meridian of the time zone, L_loc = longitude "
               "of the location (both in degrees), E = equation of time in minutes.")
    st.latex(r"\cos\theta_z = \cos\varphi\,\cos\delta\,\cos\omega + \sin\varphi\,\sin\delta")
    st.caption("Zenith angle (horizontal surface: θ = θz).")
    st.latex(
        r"\begin{aligned}\cos\theta ={}& \sin\delta\sin\varphi\cos\beta - \sin\delta\cos\varphi\sin\beta\cos\gamma \\"
        r"&+ \cos\delta\cos\varphi\cos\beta\cos\omega + \cos\delta\sin\varphi\sin\beta\cos\gamma\cos\omega \\"
        r"&+ \cos\delta\sin\beta\sin\gamma\sin\omega\end{aligned}"
    )
    st.caption("Angle of incidence on a tilted surface (used in the Incidence Angle calculator).")
    st.latex(r"\cos\omega_{ss} = -\tan\varphi\,\tan\delta \qquad N = \frac{2}{15}\,\omega_{ss}")
    st.caption("Sunset hour angle and day length N in hours. The 1/15 converts degrees into hours.")
    st.latex(r"R_b = \frac{\cos\theta}{\cos\theta_z}")
    st.caption("Beam radiation on the tilted surface relative to the horizontal.")

    st.markdown("**Extraterrestrial and clear-sky radiation**")
    st.latex(r"G_{on} = G_{sc}\left(1 + 0.033\cos\frac{360\,n}{365}\right)")
    st.caption("Extraterrestrial radiation normal to the beam, with G_sc = 1367 W/m².")
    st.latex(r"\tau_b = a_0 + a_1\,e^{-k/\cos\theta_z}")
    st.latex(
        r"a_0^* = 0.4237 - 0.00821\,(6-A)^2,\quad a_1^* = 0.5055 + 0.00595\,(6.5-A)^2,\quad "
        r"k^* = 0.2711 + 0.01858\,(2.5-A)^2"
    )
    st.caption("Hottel's method for the beam transmittance. A = altitude of the site in km. "
               "For the other climate types, a_0, a_1 and k are the starred values multiplied by "
               "the correction factors r_0, r_1 and r_k.")
    st.latex(r"\tau_d = 0.271 - 0.294\,\tau_b")
    st.caption("Liu & Jordan: diffuse transmittance on clear days.")
    st.latex(
        r"G_{cb} = \tau_b\,G_{on}\cos\theta_z \qquad G_{cd} = \tau_d\,G_{on}\cos\theta_z \qquad "
        r"G_c = G_{cb} + G_{cd}"
    )
    st.latex(r"I_c = G_c \cdot 3600\,\mathrm{s} \qquad H_c = \sum_{\text{sunrise}}^{\text{sunset}} I_c")
    st.caption("Clear-sky radiation per hour (at the midpoint of the hour) and for the whole day.")
    st.latex(r"k_T = \frac{H}{H_o}")
    st.caption("Clearness index: daily radiation divided by the daily extraterrestrial radiation.")

# ---------------------------------------------------------------- 9
with st.expander("9. Which angle do I need where?"):
    st.markdown(
        """
- **Incidence Angle calculator:** φ, δ, ω, β, γ → θ
- **Day & Hour Angle page:** date → n, solar time → ω
- **Clear-Sky Day:** location → φ and altitude, n → δ, then θz for every hour → τ_b, τ_d → G and I → H
        """
    )

st.caption("Sources: lecture slides ESE 5509 (Weeks 1–3) and Duffie & Beckman, *Solar Engineering of Thermal Processes*.")
