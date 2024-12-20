import streamlit as st
import pandas as pd
import numpy as np
from utils import *
import altair as alt

st.set_page_config(
    layout="wide"
)

conn = sql_connect('datitreni', 'sql')

st.title("Guasti e disservizi")
st.subheader("Banca dati su guasti e disservizi relativi alla rete ferroviaria piemontese")

# df = conn.query("SELECT Data, Luogo, TipoGuasto, DurataGuasto, DescrAggiuntiva AS DescrizioneAggiuntiva, NumTreniRit AS NumRit, NumTreniSopp AS NumSopp, NumTreniLim AS NumLim FROM GUASTI", ttl=0, show_spinner='Caricamento...')


date = conn.query("SELECT MIN(DATA) AS DATAMIN, MAX(DATA) AS DATAMAX FROM GUASTI;", ttl=0, show_spinner='Caricamento...')
data_min = date['DATAMIN'][0]
data_max = date['DATAMAX'][0]

durata = conn.query("SELECT MIN(DurataGuasto) AS MIN_D, MAX(DurataGuasto) AS MAX_D FROM GUASTI", ttl=0, show_spinner='Caricamento...')
durata_min = durata['MIN_D'][0]
durata_max = durata['MAX_D'][0]

intervallo_date = st.date_input("**Scegli l'intervallo di date per la tabella**", value=(data_min, data_max), min_value=data_min, max_value=data_max)
intervallo_durata = st.slider("**Scegli l'intervallo della durata dei guasti**", value=(durata_min, durata_max), min_value=durata_min, max_value=durata_max)

if len(intervallo_date) != 1:
    data_iniziale = intervallo_date[0].strftime("%Y-%m-%d")
    data_finale = intervallo_date[1].strftime("%Y-%m-%d")
    durata_iniziale = intervallo_durata[0]
    durata_finale = intervallo_durata[1]
        
    df = conn.query("SELECT Data, Luogo, TipoGuasto, DurataGuasto, DescrAggiuntiva AS DescrizioneAggiuntiva, NumTreniRit AS NumRit, NumTreniSopp AS NumSopp, NumTreniLim AS NumLim FROM GUASTI", ttl=0, show_spinner='Caricamento...')
      
    df['Data'] = pd.to_datetime(df['Data'])
    mask = (df['Data'] >= data_iniziale) & (df['Data'] <= data_finale) & (df['DurataGuasto'] >= durata_iniziale) & (df['DurataGuasto'] <= durata_finale)
    df = df.loc[mask]
    df['Data'] = df['Data'].dt.date

    if df.empty:
        st.warning('Nessun dato trovato.', icon='⚠️')
        st.stop()
    
    
    st.dataframe(df, use_container_width=True)

st.info("**NumRit**, **NumSopp** e **NumLim** si riferiscono al numero di treni con ritardo, soppressione o limitazione del percorso causati direttamente dal guasto all'infrastruttura. La **durata del guasto** è espressa in minuti.\n\nE' possibile scaricare la tabella in formato CSV tramite l'apposito pulsante posizionato in alto a destra, visualizzabile al passaggio del cursore del mouse sulla tabella. Tramite il pulsante a fianco è invece possibile effettuare una ricerca nelle celle della tabella.")
