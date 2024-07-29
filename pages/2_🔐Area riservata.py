import streamlit as st
import pandas as pd
import numpy as np
from utils import *
import altair as alt
import hmac
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Area riservata",
    page_icon="🔐",
    layout="wide"
)

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["credenziali"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password errata")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# La pagina inizia da qui \/

conn = sql_connect('datitreni', 'sql')

st.title("Accesso completo al database CORSE")

elenco_num_treni = conn.query('SELECT DISTINCT NumTreno FROM CORSE;', ttl=0, show_spinner=False)
num_treni_lista = elenco_num_treni['NumTreno'].tolist()
scelta_treno = st.selectbox("**Seleziona il numero del treno**", num_treni_lista, index=None, placeholder='Scegli il numero del treno...')

if scelta_treno != None:        # scelta date per visualizzazione dataframe
    date=conn.query(f"SELECT MIN(DATA) AS DATAMIN, MAX(DATA) AS DATAMAX FROM CORSE WHERE NumTreno={scelta_treno};", ttl=0)
    data_min = date['DATAMIN'][0]
    data_max = date['DATAMAX'][0]

    intervallo_date = st.date_input("**Scegli l'intervallo di date per la tabella**",value=(data_min,data_max),min_value=data_min,max_value=data_max)

    if len(intervallo_date) != 1:
        data_iniziale = intervallo_date[0].strftime("%Y-%m-%d")
        data_finale = intervallo_date[1].strftime("%Y-%m-%d")
        
        df = conn.query(f"SELECT * FROM CORSE WHERE NumTreno={scelta_treno};", ttl=0)
        
        df['Data'] = pd.to_datetime(df['Data'])
        mask = (df['Data'] >= data_iniziale) & (df['Data'] <= data_finale)
        df = df.loc[mask]
        df['Data'] = df['Data'].dt.date
        
        df['Sopp'] = df['Sopp'].replace(1, "SI'").replace(0, "NO")
        df['Var'] = df['Var'].replace(1, "SI'").replace(0, "NO")

        colormap_original = plt.cm.get_cmap('RdYlGn')
        reversed_map = colormap_original.reversed() 

        def make_pretty(styler):
            styler.background_gradient(axis=None, vmin=-6, vmax=14, cmap=reversed_map, subset="Rit")
            styler.format(precision=0, thousands="", decimal=",")
            styler.highlight_null(color='purple')
            return styler

        df = df.style.pipe(make_pretty)
        st.dataframe(df, use_container_width=True)

st.divider()
st.title("Generatore query per inserimento guasti nel db")
with st.form("my_form"):
    st.write("Modulo di generazione query:")
    data = st.date_input("Inserisci la data del guasto:")
    loc = st.text_input("Inserisci la località del guasto:", value=None, max_chars=30)
    tipo = st.text_input("Inserisci il tipo del guasto:", value=None, max_chars=80)
    durata = st.number_input("Inserisci la durata del guasto (in minuti):", value=None, min_value=0, max_value=5000, step=1)
    desc = st.text_input("Inserisci la descrizione aggiuntiva (opzionale):", value=None, max_chars=80)
    n_rit = st.number_input("Inserisci il numero di ritardi:", value=None, min_value=0, max_value=100, step=1)
    n_sopp = st.number_input("Inserisci il numero di soppressioni:", value=None, min_value=0, max_value=100, step=1)
    n_lim = st.number_input("Inserisci il numero di treni limitati nel percorso:", value=None, min_value=0, max_value=100, step=1)

    submitted = st.form_submit_button("Genera query")

    if submitted:
        if data == None or loc == None or tipo == None or durata == None or n_rit == None or n_sopp == None or n_lim == None:
            st.error("Compila i campi correttamente. Mancano delle informazioni.")
        else:
            if desc == None:
                desc = 'NULL'
            query = f"INSERT INTO GUASTI (Data,Luogo,TipoGuasto,DurataGuasto,DescrAggiuntiva,NumTreniRit,NumTreniSopp,NumTreniLim) VALUES ('{data}','{loc}','{tipo}',{durata},'{desc}',{n_rit},{n_sopp},{n_lim});"
               
            st.subheader("Query da inserire:")
            st.markdown(f":blue-background[{query}]")
