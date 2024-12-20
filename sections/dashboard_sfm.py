import streamlit as st
import pandas as pd
import numpy as np
from utils import *
from utils_sfm_page import *
import altair as alt

st.set_page_config(
    layout="wide"
)

conn = sql_connect('datitreni', 'sql')

st.image("assets/logo_sfm.png", width=300)

with st.container(border=True):
    metrics_sfm_tot_ieri(conn)

with st.container(border=True):
    metrics_sfm_tot_sett(conn)

with st.container(border=True):
    st.subheader("Storico con dati aggregati per settimane")
    sfm_grafico(conn)

with st.expander("Statistiche per intervallo di date a scelta"):
    metrics_sfm_scelta(conn)    

with st.expander("Mappa linee SFM"):
    st.image("assets/mappa_sfm_12_24.jpg")

st.markdown(f"**Nota:** Nei grafici, **:green-background[sfm3]** si riferisce alla relazione Torino-Bardonecchia; **:green-background[sfm3b]** si riferisce alla relazione Torino-Susa")