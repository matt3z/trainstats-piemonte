import streamlit as st
from utils import *
from utils_homepage import *
import altair as alt
import datetime
import pandas as pd
import pydeck as pdk
import numpy as np

st.set_page_config(
    layout="wide"
)

st.sidebar.title('TrainStats Piemonte')
st.sidebar.header(':blue[Benvenuto!]')
st.sidebar.markdown("In questo portale si possono trovare\nstatistiche e informazioni\nsulla circolazione dei treni\nin Piemonte\n\nPer aiuto sull'utilizzo\ndel portale, visitare\nla pagina informazioni\n\n\nStato connessione DB:")

conn = sql_connect('datitreni', 'sql')

st.title("Homepage")
st.subheader('Statistiche sulle linee ferroviarie piemontesi')

tab1, tab2, tab3 = st.tabs(['📈 Statistiche e grafici', '🚄 Ricerca per numero treno', '🗺️ Mappa delle stazioni'])

with tab1:
    ricerca_per_linea(conn)


with tab2:
    ricerca_per_treno(conn)


with tab3:      # mappa
    st.subheader('Mappa')
    st.markdown("Nella mappa è visualizzabile il ritardo medio di termine corsa dei treni per ogni stazione capolinea:")
    visualizza_mappa_stazioni(conn)
    
