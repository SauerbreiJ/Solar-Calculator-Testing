"""Entry point. Run with:  streamlit run app.py

Navigation + the shared sidebar (site, date, surface) live here. Each tool is one file
in pages/, all calculations are in the solar/ package.
"""
import streamlit as st

from ui.site import site_sidebar

st.set_page_config(page_title="Solar Tools", page_icon="☀️")

pg = st.navigation({
    "Start": [
        st.Page("pages/0_introduction.py", title="Introduction", icon="📖", default=True),
    ],
    "Geometry": [
        st.Page("pages/2_sun_position.py", title="Sun Position", icon="🧭"),
        st.Page("pages/1_incidence.py", title="Incidence Angle", icon="☀️"),
        st.Page("pages/4_rb.py", title="Beam Ratio Rb", icon="📐"),
    ],
    "Radiation": [
        st.Page("pages/5_extraterrestrial.py", title="Extraterrestrial", icon="🌍"),
        st.Page("pages/3_clear_sky.py", title="Clear-Sky Day", icon="🌤️"),
        st.Page("pages/6_sunshine.py", title="Sunshine Hours → H̄", icon="🌥️"),
        st.Page("pages/7_split.py", title="Beam/Diffuse Split", icon="🔀"),
        st.Page("pages/8_daily_hourly.py", title="Daily → Hourly", icon="⏱️"),
        st.Page("pages/9_tilted.py", title="Tilted Surface", icon="📊"),
    ],
    "Tools": [
        st.Page("pages/10_full_chain.py", title="Full Chain", icon="🔗"),
    ],
})
site_sidebar()
pg.run()
