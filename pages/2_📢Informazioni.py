import streamlit as st
import pandas as pd
import numpy as np
from utils import *
import altair as alt

st.set_page_config(
    page_title="Informazioni",
    page_icon="📢",
    layout="wide"
)

st.title("Informazioni sul sito")

st.subheader('Come usare il sito:')
st.markdown("Nella homepage sono presenti due schede: **'Statistiche e grafici'** e **'Mappa'**:")
st.markdown("Nella scheda **'Statistiche e grafici'**, selezionare una delle linee disponibili dal menù a tendina. Verranno visualizzate le statistiche generali relative all'ultima settimana e dei grafici per i quali è selezionabile l'intervallo di date attraverso l'apposito menù.")
st.markdown("Nella scheda **'Mappa'** è presente una mappa con evidenziate le stazioni e le linee. È possibile selezionare se visualizzare i dati relativi alle linee oppure alle stazioni al passaggio del mouse, attraverso il selettore presente sopra alla cartina. La media dei ritardi, per quanto riguarda le stazioni, si riferisce ai ritardi dei treni in arrivo. Anche il ritardo medio di ogni linea è calcolato in base all'orario di arrivo a destinazione del treno.")

st.subheader('Info:')
st.info("Webapp sviluppata in Python grazie a Streamlit.\n\nI dati su cui sono elaborate le statistiche sono provenienti da Viaggiatreno.\n\nPer contatti: info@ferroviebiellesi.it\n\n© Matteo Manfrin - 2024")

st.subheader('Changelog:')
st.info("**30/07/2024 - Versione 1.1**\n\nAggiunta sezione guasti e disservizi, implementate statistiche sulla puntualità per il periodo di date selezionato, inserito nuovo grafico relativo alla media di ritardi per treno. Effettuati diversi miglioramenti al codice.\n\n**15/06/2024 - Versione 1.0**\n\nVersione iniziale del portale.")
