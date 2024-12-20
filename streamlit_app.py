import streamlit as st
from utils import *

homepage = st.Page(
    page = "pages/homepage.py",
    title = "Homepage",
    icon="🏠",
    default=True
)

dashboard_sfm = st.Page(
    page = "pages/dashboard_sfm.py",
    title = "Dashboard SFM",
    icon="🚉"
)

guasti_disservizi = st.Page(
    page = "pages/guasti_e_disservizi.py",
    title = "Guasti e disservizi",
    icon="⛔"
)

informazioni = st.Page(
    page = "pages/informazioni.py",
    title = "Informazioni",
    icon="📢"
)

area_riservata = st.Page(
    page = "pages/area_riservata.py",
    title = "Area riservata",
    icon="🔐"
)

otc_focus = st.Page(
    page = "pages/otc_focus.py",
    title = "SFM 4-6-7 Focus",
    icon="🔐"
)

pg = st.navigation(
    {
        "Statistiche": [homepage, dashboard_sfm, guasti_disservizi],
        "Altro": [informazioni, area_riservata]
    }
)

pg.run()
