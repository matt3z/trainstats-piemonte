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
    df = conn.query('SELECT NOMELINEA FROM LINEE ORDER BY NOMELINEA;', ttl=0, show_spinner=False)
    linee_nome = df['NOMELINEA'].tolist()

    scelta_linea = st.selectbox("Seleziona la linea da visualizzare", linee_nome, index=None, placeholder='Scegli la linea...')
    with st.container(border=True):     # streamlit metric per statistiche sull'ultima settimana
        if scelta_linea != None:
            df2 = conn.query(f"SELECT CodLinea FROM LINEE WHERE NomeLinea='{scelta_linea}';", ttl=0, show_spinner=False)
            scelta_linea_codice = df2['CodLinea'][0]        # query sql per dati sull'ultima settimana \/
            puntualita, puntualita_scorsa_sett = calcola_df_puntualita_iniziali(conn, scelta_linea_codice)
            if puntualita['DATA_DA'][0] == None:
                st.warning("Nessun dato trovato.",icon='⚠️')    # controllo sull'esistenza di dati per la linea selezionata
                st.stop()
            else:
                data_da, data_a, punt_val, r5_val, r15_val, sopp_val, var_val, treni_tot_val = valori_puntualita_iniziali(puntualita)
                if puntualita_scorsa_sett['DATA_DA'][0] == None:
                    st.subheader(f"Riepilogo degli ultimi 7 giorni (dal {data_da} al {data_a}):")
                    colm1,colm2,colm3, colm4, colm5=st.columns(5)
                    colm1.metric(label="Puntualità", value=f'{round(punt_val,2)}%')
                    colm2.metric(label="n° Ritardi da 5 a 14 min", value=r5_val)
                    colm3.metric(label="n° Ritardi superiori a 15 min", value=r15_val)
                    colm4.metric(label="n° Treni soppressi", value=sopp_val)
                    colm5.metric(label="n° Treni variati", value=var_val)
                    st.markdown(f"su **:blue-background[{treni_tot_val}]** treni totali")
                else:
                    delta_or_val, delta_r5_val, delta_r15_val, delta_sopp_val, delta_var_val = valori_delta_puntualita(puntualita_scorsa_sett, punt_val, r5_val, r15_val, sopp_val, var_val)
                    st.subheader(f"Riepilogo degli ultimi 7 giorni (dal {data_da} al {data_a}):")
                    colm1,colm2,colm3, colm4, colm5=st.columns(5)
                    colm1.metric(label="Puntualità", value=f'{round(punt_val,2)}%', delta=f'{round(delta_or_val,2)}%')
                    colm2.metric(label="n° Ritardi da 5 a 14 min ", value=r5_val, delta=delta_r5_val, delta_color='inverse')
                    colm3.metric(label="n° Ritardi superiori a 15 min ", value=r15_val, delta=delta_r15_val, delta_color='inverse')
                    colm4.metric(label="n° Treni soppressi", value=sopp_val, delta=delta_sopp_val, delta_color='inverse')
                    colm5.metric(label="n° Treni variati", value=var_val, delta=delta_var_val, delta_color='inverse')
                    st.markdown(f"su **:blue-background[{treni_tot_val}]** treni totali")

    
    if scelta_linea != None:        # scelta date per visualizzazione grafici
        date=conn.query(f"SELECT MIN(DATA) AS DATAMIN, MAX(DATA) AS DATAMAX FROM CORSE, TRENI WHERE TRENI.NumTreno=CORSE.NumTreno AND LINEA={scelta_linea_codice};", ttl=0, show_spinner="Caricamento...")
        data_min = date['DATAMIN'][0]
        data_max = date['DATAMAX'][0]

        intervallo_date = st.date_input("Scegli l'intervallo di date per i grafici",value=(data_min,data_max),min_value=data_min,max_value=data_max)

    if scelta_linea != None and len(intervallo_date) != 1:
        df2 = conn.query(f"SELECT CodLinea FROM LINEE WHERE NomeLinea='{scelta_linea}';", ttl=0, show_spinner=False)    # estraggo il codice linea dal nome
        scelta_linea_codice = df2['CodLinea'][0]

        chart_media, data_media = grafico_media(conn, intervallo_date, scelta_linea_codice)
        
        if data_media.empty:
            st.warning("Nessun dato trovato.",icon='⚠️')
        else:
            with st.container(border=True):     # statistiche relative a date - calcola puntualità tra date selezionate e visualizza metric
                punt_int_val, r5_int_val, r15_int_val, sopp_int_val, var_int_val, treni_tot_int_val = metrics_intervallo(conn, intervallo_date, scelta_linea_codice)
                st.subheader('Riepilogo relativo alle date selezionate:')
                colm1,colm2,colm3, colm4, colm5 = st.columns(5)
                colm1.metric(label="Puntualità", value=f'{round(punt_int_val,2)}%')
                colm2.metric(label="n° Ritardi da 5 a 14 min", value=r5_int_val)
                colm3.metric(label="n° Ritardi superiori a 15 min", value=r15_int_val)
                colm4.metric(label="n° Treni soppressi", value=sopp_int_val)
                colm5.metric(label="n° Treni variati", value=var_int_val)
                st.markdown(f"su **:blue-background[{treni_tot_int_val}]** treni totali")

            with st.container(border=True):
                st.subheader('Puntualità e numero di ritardi/soppressioni:')
                col1, col2 = st.columns([4,1])
                chart_percent, data_percent = grafico_percent(conn, intervallo_date, scelta_linea_codice)
                with col1:
                    st.altair_chart(chart_percent, theme='streamlit', use_container_width=True)
                with col2:
                    st.dataframe(data_percent, height=400, use_container_width=True, column_config={"PERC_ORARIO": st.column_config.NumberColumn(format="%.2f")})
            
            with st.container(border=True):
                st.subheader('Media dei ritardi totali raggruppata per giorno:')
                col3, col4 = st.columns([4,1])
                with col3:
                    st.altair_chart(chart_media, theme='streamlit', use_container_width=True)
                with col4:
                    col4.dataframe(data_media, height=400, use_container_width=True, column_config={"MEDIA_RIT": st.column_config.NumberColumn(format="%.2f")})

            with st.container(border=True):
                st.subheader('Numero di ritardi/soppressioni per treno:')
                chart_rit_treno, data_rit_treno = grafico_per_num_treno(conn, intervallo_date, scelta_linea_codice)
                st.altair_chart(chart_rit_treno, theme='streamlit', use_container_width=True)

            with st.container(border=True):
                st.subheader('Media dei ritardi totali raggruppata per treno:')
                chart_media_per_num_treno, data_media_per_num_treno = grafico_media_per_num_treno(conn, intervallo_date, scelta_linea_codice)
                st.altair_chart(chart_media_per_num_treno, theme='streamlit', use_container_width=True)


with tab2:
    ricerca_per_treno(conn)


with tab3:      # mappa
    st.subheader('Mappa')
    st.markdown("Nella mappa è visualizzabile il ritardo medio di termine corsa dei treni per ogni stazione capolinea:")
    visualizza_mappa_stazioni(conn)
    
