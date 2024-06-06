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

conn = sql_connect('datitreni', 'sql')

st.title("Informazioni sul sito")
st.info("Webapp sviluppata in Python grazie a Streamlit.\n\nI dati su cui sono elaborate le statistiche sono provenienti dalle API di Viaggiatreno.\n\nPer contatti: info@ferroviebiellesi.it\n\n© Matteo Manfrin - 2024")
