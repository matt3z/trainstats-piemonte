import streamlit as st
import pandas as pd
import numpy as np
from utils import *
import altair as alt

st.set_page_config(
    layout="wide"
)

st.title("Informazioni sul sito")

st.subheader("Per l'utilizzo del sito:")
st.markdown("Nella homepage sono presenti due schede: **'Statistiche e grafici'** e **'Mappa'**:")
st.markdown("- Nella scheda **'Statistiche e grafici'**, selezionare una delle linee disponibili dal menù a tendina. Verranno visualizzate le statistiche generali relative all'ultima settimana e dei grafici per i quali è selezionabile l'intervallo di date attraverso l'apposito menù.\n- Nella scheda **'Mappa'** è presente una mappa con evidenziate le stazioni. È possibile visualizzare i dati del ritardo medio dei treni che terminano la corsa nelle relative stazioni, al passaggio del mouse sull'indicatore.")
st.markdown("Nel portale sono inoltre presenti le sezioni **'Dashboard SFM'** e **'Guasti e disservizi'**, raggiungibili attraverso la barra laterale:")
st.markdown("- Nella sezione **'Dashboard SFM'**, sono presenti statistiche e grafici relativi all'intero Servizio Ferroviario Metropolitano, per permetterne un monitoraggio semplice e immediato.\n- Nella sezione **'Guasti e disservizi'**, è presente una banca dati costantemente aggiornata sui guasti all'infrastruttura ferroviaria piemontese.")

st.subheader('Info:')
st.info("Webapp sviluppata in Python grazie a Streamlit.\n\nI dati su cui sono elaborate le statistiche sono provenienti da Viaggiatreno.\n\nPer contatti: info@ferroviebiellesi.it\n\n© Matteo Manfrin - 2024")

st.subheader('Changelog:')
st.info("**20/12/2024 - Versione 1.2**\n\nAggiunta sezione Dashboard SFM, per un monitoraggio più semplice e immediato delle linee SFM. Aggiornato Streamlit alla versione 1.41, e implementato il nuovo sistema per la gestione delle app multipagina. Effettuati alcuni miglioramenti al codice.\n\n**30/07/2024 - Versione 1.1**\n\nAggiunta sezione guasti e disservizi, implementate statistiche sulla puntualità per il periodo di date selezionato, inserito nuovo grafico relativo alla media di ritardi per treno. Effettuati diversi miglioramenti al codice.\n\n**15/06/2024 - Versione 1.0**\n\nVersione iniziale del portale.")
