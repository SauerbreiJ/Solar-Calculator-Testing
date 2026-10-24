"""Entry point. Run with:  streamlit run app.py

Only the navigation lives here. Each tool is one file in pages/,
all calculations are in the solar/ package.
"""
import streamlit as st

st.set_page_config(page_title="Solar Tools", page_icon="☀️")

pg = st.navigation({
    "Start": [
        st.Page("pages/0_introduction.py", title="Introduction", icon="📖", default=True),
    ],
    "Geometry": [
        st.Page("pages/1_incidence.py", title="Incidence Angle", icon="☀️"),
        st.Page("pages/2_day_hour.py", title="Day & Hour Angle", icon="📅"),
    ],
    "Radiation": [
        st.Page("pages/3_clear_sky.py", title="Clear-Sky Day", icon="🌤️"),
    ],
})
pg.run()
