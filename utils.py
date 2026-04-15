import streamlit as st
import altair as alt
from datetime import datetime as dt

def sql_connect(nomeconn, tipo):
    try:
        conn = st.connection(nomeconn, type=tipo)
        conn.query('SELECT * FROM LINEE LIMIT 0;', ttl=0, show_spinner=False)
        st.sidebar.success("Connesso al DB")
        return conn
    except:
        st.sidebar.error("Connessione al DB\nnon riuscita")

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

def converti_data_ora(timestamp):
    timestamp = timestamp/1000
    dt_object = dt.fromtimestamp(timestamp)
    return dt_object
