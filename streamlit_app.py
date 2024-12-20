import streamlit as st
from utils import *

homepage = st.Page(
    page = "sections/homepage.py",
    title = "Homepage",
    icon="🏠",
    default=True
)

dashboard_sfm = st.Page(
    page = "sections/dashboard_sfm.py",
    title = "Dashboard SFM",
    icon="🚉"
)

guasti_disservizi = st.Page(
    page = "sections/guasti_e_disservizi.py",
    title = "Guasti e disservizi",
    icon="⛔"
)

informazioni = st.Page(
    page = "sections/informazioni.py",
    title = "Informazioni",
    icon="📢"
)

area_riservata = st.Page(
    page = "sections/area_riservata.py",
    title = "Area riservata",
    icon="🔐"
)

pg = st.navigation(
    {
        "Statistiche": [homepage, dashboard_sfm, guasti_disservizi],
        "Altro": [informazioni, area_riservata]
    }
)

pg.run()
