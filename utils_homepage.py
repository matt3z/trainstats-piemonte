import streamlit as st
from utils import *
import altair as alt
import datetime
import pandas as pd
import pydeck as pdk
import plotly.express as px
import numpy as np
import json


# TAB 1 - RICERCA PER LINEA

def ricerca_per_linea(conn):
    df = conn.query('SELECT NomeLinea FROM LINEE ORDER BY NomeLinea;', ttl=500, show_spinner=False)
    linee_nome = df['NomeLinea'].tolist()

    scelta_linea = st.selectbox("Seleziona la linea da visualizzare", linee_nome, index=None, placeholder='Scegli la linea...')
    #with st.container(border=True):     # streamlit metric per statistiche sull'ultima settimana
    if scelta_linea != None:
        with st.container(border=True):
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
        date=conn.query(f"SELECT MIN(DATA) AS DATAMIN, MAX(DATA) AS DATAMAX FROM CORSE WHERE LINEA={scelta_linea_codice};", ttl=0, show_spinner="Caricamento...")
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
                    st.altair_chart(chart_percent, theme='streamlit', width='stretch')
                with col2:
                    st.dataframe(data_percent, height=400, width='stretch', column_config={"PERC_ORARIO": st.column_config.NumberColumn(format="%.2f")})
            
            with st.container(border=True):
                st.subheader('Media dei ritardi totali raggruppata per giorno:')
                col3, col4 = st.columns([4,1])
                with col3:
                    st.altair_chart(chart_media, theme='streamlit', width='stretch')
                with col4:
                    col4.dataframe(data_media, height=400, width='stretch', column_config={"MEDIA_RIT": st.column_config.NumberColumn(format="%.2f")})

            with st.container(border=True):
                st.subheader('Numero di ritardi/soppressioni per treno:')
                chart_rit_treno, data_rit_treno = grafico_per_num_treno(conn, intervallo_date, scelta_linea_codice)
                st.altair_chart(chart_rit_treno, theme='streamlit', width='stretch')

            with st.container(border=True):
                st.subheader('Media dei ritardi totali raggruppata per treno:')
                chart_media_per_num_treno, data_media_per_num_treno = grafico_media_per_num_treno(conn, intervallo_date, scelta_linea_codice)
                st.altair_chart(chart_media_per_num_treno, theme='streamlit', width='stretch')



# funzioni di supporto tab1

def grafico_percent(conn, intervallo_date, scelta_linea_codice):
    data=conn.query(f"with TabTot AS (SELECT DATA, COUNT(*) AS NUMTOT FROM CORSE WHERE Linea={int(scelta_linea_codice)} AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA), TabOrario AS (SELECT DATA, COUNT(*) AS ORARIO FROM CORSE WHERE Linea={int(scelta_linea_codice)} AND RitArrivo IS NOT NULL AND RitArrivo<5 AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA), TabRit5 AS (SELECT DATA, COUNT(*) AS RIT5 FROM CORSE WHERE Linea={int(scelta_linea_codice)} AND RitArrivo>=5 AND RitArrivo<15 AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA), TabRit15 AS (SELECT DATA, COUNT(*) AS RIT15 FROM CORSE AS C WHERE Linea={int(scelta_linea_codice)} AND RitArrivo>=15 AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA), TabSopp AS (SELECT DATA, COUNT(*) AS SOPP FROM CORSE AS C WHERE Linea={int(scelta_linea_codice)} AND Sopp=1 AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA), TabVar AS (SELECT DATA, COUNT(*) AS VAR FROM CORSE AS C WHERE Linea={int(scelta_linea_codice)} AND Var=1 AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA) SELECT TT.DATA, IFNULL((ORARIO/NUMTOT)*100,0) AS PERC_ORARIO, IFNULL(RIT5,0) AS N_RIT5, IFNULL(RIT15,0) AS N_RIT15, IFNULL(SOPP,0) AS N_SOPP, IFNULL(VAR,0) AS N_VAR FROM TABTOT AS TT LEFT JOIN TABORARIO AS TOR ON TT.DATA=TOR.DATA LEFT JOIN TABRIT5 AS TR5 ON TT.DATA=TR5.DATA LEFT JOIN TABRIT15 AS TR15 ON TT.DATA=TR15.DATA LEFT JOIN TABSOPP AS TS ON TT.DATA=TS.DATA LEFT JOIN TABVAR AS TV ON TT.DATA=TV.DATA;", ttl=0, show_spinner="Caricamento...")
    
    scale = alt.Scale(domain=['PERC_ORARIO','N_RIT5', 'N_RIT15', 'N_SOPP', 'N_VAR'], range=['#4daf4a','yellow', 'orange', 'red', 'purple'])

    base = alt.Chart(data).encode(alt.X('DATA:T', axis=alt.Axis(title=None)))

    bars = base.transform_fold(
        ['N_RIT5', 'N_RIT15', 'N_SOPP', 'N_VAR'],
    ).mark_bar().encode(
        y='value:Q',
        color=alt.Color('key:N', scale=scale).title('Legenda'))
    line = base.transform_fold(['PERC_ORARIO']).mark_line(interpolate="monotone").encode(alt.Y('PERC_ORARIO:Q', axis=alt.Axis(title=None)), color=alt.Color('key:N', scale=scale))

    chart = (bars + line).properties(width=600)

    return chart, data


def grafico_media(conn, intervallo_date, scelta_linea_codice):
    data = conn.query(f"SELECT DATA, IFNULL(AVG(RitArrivo),0) AS MEDIA_RIT FROM CORSE WHERE DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' AND LINEA={int(scelta_linea_codice)} GROUP BY DATA;",
                            ttl=0, show_spinner="Caricamento...")
    
    scale = alt.Scale(domain=['MEDIA_RIT'], range=['#6baed6'])
    chart = alt.Chart(data).transform_fold(['MEDIA_RIT']).mark_line(interpolate="monotone").encode(alt.X("DATA:T", axis=alt.Axis(title=None)), alt.Y("MEDIA_RIT:Q", axis=alt.Axis(title=None)), color=alt.Color('key:N', scale=scale).title('Legenda'))
    
    return chart, data


def grafico_per_num_treno(conn, intervallo_date, scelta_linea_codice):
    data = conn.query(f"with TabTreni AS (SELECT NumTreno FROM CORSE WHERE LINEA={int(scelta_linea_codice)} AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY NUMTRENO), TabRit5 AS (SELECT NumTreno, COUNT(*) AS RIT5 FROM CORSE WHERE Linea={int(scelta_linea_codice)} AND RitArrivo>=5 AND RitArrivo<15 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY NumTreno), TabRit15 AS (SELECT NumTreno, COUNT(*) AS RIT15 FROM CORSE WHERE Linea={int(scelta_linea_codice)} AND RitArrivo>=15 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY NumTreno), TabSopp AS (SELECT NumTreno, COUNT(*) AS SOPP FROM CORSE WHERE Linea={int(scelta_linea_codice)} AND Sopp=1 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY NumTreno), TabVar AS (SELECT NumTreno, COUNT(*) AS VAR FROM CORSE WHERE Linea={int(scelta_linea_codice)} AND Var=1 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY NumTreno) SELECT TT.NumTreno AS NUMTRENO, IFNULL(RIT5,0) AS N_RIT5, IFNULL(RIT15,0) AS N_RIT15, IFNULL(SOPP,0) AS N_SOPP, IFNULL(VAR,0) AS N_VAR FROM TABTreni AS TT LEFT JOIN TABRIT5 AS TR5 ON TT.NumTreno=TR5.NumTreno LEFT JOIN TABRIT15 AS TR15 ON TT.NumTreno=TR15.NumTreno LEFT JOIN TABSOPP AS TS ON TT.NumTreno=TS.NumTreno LEFT JOIN TABVAR AS TV ON TT.NumTreno=TV.NumTreno;",
                            ttl=0, show_spinner="Caricamento...")

    data['NUMTRENO'] = data.NUMTRENO.astype('str')
    
    scale = alt.Scale(domain=['N_RIT5', 'N_RIT15', 'N_SOPP', 'N_VAR'], range=['yellow', 'orange', 'red', 'purple'])
    chart = alt.Chart(data).transform_fold(['N_RIT5', 'N_RIT15', 'N_SOPP', 'N_VAR']).mark_bar(size=15).encode(alt.X("NUMTRENO", axis=alt.Axis(title=None)), alt.Y("value:Q", axis=alt.Axis(title=None)), color=alt.Color('key:N', scale=scale).title('Legenda'))
   
    return chart, data


def grafico_media_per_num_treno(conn, intervallo_date, scelta_linea_codice):
    data = conn.query(f"SELECT NumTreno AS NUMTRENO, AVG(RitArrivo) AS MEDIA_RIT FROM CORSE WHERE Linea={int(scelta_linea_codice)} AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY NumTreno;", ttl=0, show_spinner="Caricamento...")
    
    data['NUMTRENO'] = data.NUMTRENO.astype('str')

    scale = alt.Scale(domain=['MEDIA_RIT'], range=['#6baed6'])
    chart = alt.Chart(data).transform_fold(['MEDIA_RIT']).mark_bar(size=15).encode(alt.X("NUMTRENO", axis=alt.Axis(title=None)), alt.Y("MEDIA_RIT:Q", axis=alt.Axis(title=None)), color=alt.Color('key:N', scale=scale).title('Legenda'))

    return chart, data


def metrics_intervallo(conn, intervallo_date, scelta_linea_codice):
    data = conn.query(f"WITH TabGroupDay AS (SELECT CORSE.Data as DATE, COUNT(*) AS NUMTOT FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)} AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabOr AS (SELECT CORSE.Data as DATE, COUNT(*) AS ORARIO FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)} AND RitArrivo IS NOT NULL AND RitArrivo<5 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabR5 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT5 FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)} AND RitArrivo IS NOT NULL AND RitArrivo>=5 AND RitArrivo<15 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabR15 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT15 FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)} AND RitArrivo IS NOT NULL AND RitArrivo>=15 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabSopp AS (SELECT CORSE.Data as DATE, COUNT(*) AS SOPP FROM CORSE, TRENI WHERE CORSE.NumTreno=TRENI.NumTreno AND TRENI.Linea={int(scelta_linea_codice)} AND CORSE.Sopp=1 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabVar AS (SELECT CORSE.Data as DATE, COUNT(*) AS VAR FROM CORSE, TRENI WHERE CORSE.NumTreno=TRENI.NumTreno AND TRENI.Linea={int(scelta_linea_codice)} AND CORSE.Var=1 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabDati1 AS (SELECT TGD.DATE AS DATE, NUMTOT, IFNULL(ORARIO,0) AS ORARIO, IFNULL(RIT5,0) AS RIT5, IFNULL(RIT15,0) AS RIT15, IFNULL(SOPP,0) AS SOPP, IFNULL(VAR,0) AS VAR FROM TabGroupDay AS TGD LEFT JOIN TabOr AS TOR ON TGD.DATE=TOR.DATE LEFT JOIN TabR5 AS TR5 ON TGD.DATE=TR5.DATE LEFT JOIN TabR15 AS TR15 ON TGD.DATE=TR15.DATE LEFT JOIN TabSopp AS TSP ON TGD.DATE=TSP.DATE LEFT JOIN TabVar as TVR ON TGD.DATE=TVR.DATE) SELECT MIN(DATE) AS DATA_DA, MAX(DATE) AS DATA_A, (SUM(ORARIO)/SUM(NUMTOT))*100 AS PUNTUALITA, SUM(RIT5) AS RIT5, SUM(RIT15) AS RIT15, SUM(SOPP) AS SOPP, SUM(VAR) AS VAR, SUM(NUMTOT) AS TRENI_TOT FROM TabDati1;", ttl=0, show_spinner="Caricamento...")
    punt_val = data['PUNTUALITA'][0]
    r5_val = int(data['RIT5'][0])
    r15_val = int(data['RIT15'][0])
    sopp_val = int(data['SOPP'][0])
    var_val = int(data['VAR'][0])
    treni_tot_val = int(data['TRENI_TOT'][0])

    return punt_val, r5_val, r15_val, sopp_val, var_val, treni_tot_val


def calcola_df_puntualita_iniziali(conn, scelta_linea_codice):
    puntualita = conn.query(f"WITH TabMaxDate AS (SELECT MAX(DATA) AS DATAMASSIMA FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)}), TabGroupDay AS (SELECT CORSE.Data as DATE, COUNT(*) AS NUMTOT FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)} AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabOr AS (SELECT CORSE.Data as DATE, COUNT(*) AS ORARIO FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)} AND RitArrivo IS NOT NULL AND RitArrivo<5 AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabR5 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT5 FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)} AND RitArrivo IS NOT NULL AND RitArrivo>=5 AND RitArrivo<15 AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabR15 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT15 FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)} AND RitArrivo IS NOT NULL AND RitArrivo>=15 AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabSopp AS (SELECT CORSE.Data as DATE, COUNT(*) AS SOPP FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)} AND CORSE.Sopp=1 AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabVar AS (SELECT CORSE.Data as DATE, COUNT(*) AS VAR FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)} AND CORSE.Var=1 AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabDati1 AS (SELECT TGD.DATE AS DATE, NUMTOT, IFNULL(ORARIO,0) AS ORARIO, IFNULL(RIT5,0) AS RIT5, IFNULL(RIT15,0) AS RIT15, IFNULL(SOPP,0) AS SOPP, IFNULL(VAR,0) AS VAR FROM TabGroupDay AS TGD LEFT JOIN TabOr AS TOR ON TGD.DATE=TOR.DATE LEFT JOIN TabR5 AS TR5 ON TGD.DATE=TR5.DATE LEFT JOIN TabR15 AS TR15 ON TGD.DATE=TR15.DATE LEFT JOIN TabSopp as TSP ON TGD.DATE=TSP.DATE LEFT JOIN TabVar as TVR ON TGD.DATE=TVR.DATE) SELECT MIN(DATE) AS DATA_DA, MAX(DATE) AS DATA_A, (SUM(ORARIO)/SUM(NUMTOT))*100 AS PUNTUALITA, SUM(RIT5) AS RIT5, SUM(RIT15) AS RIT15, SUM(SOPP) AS SOPP, SUM(VAR) AS VAR, SUM(NUMTOT) AS TRENI_TOT FROM TabDati1;", ttl=0, show_spinner="Caricamento...")
    puntualita_scorsa_sett = conn.query(f"WITH TabMaxDate AS (SELECT MAX(DATA) AS DATAMASSIMA FROM CORSE WHERE CORSE.Linea={int(scelta_linea_codice)}), TabGroupDay AS (SELECT CORSE.Data as DATE, COUNT(*) AS NUMTOT FROM CORSE, TabMaxDate WHERE CORSE.Linea={int(scelta_linea_codice)} AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabOr AS (SELECT CORSE.Data as DATE, COUNT(*) AS ORARIO FROM CORSE, TabMaxDate WHERE CORSE.Linea={int(scelta_linea_codice)} AND RitArrivo IS NOT NULL AND RitArrivo<5 AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabR5 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT5 FROM CORSE, TabMaxDate WHERE CORSE.Linea={int(scelta_linea_codice)} AND RitArrivo IS NOT NULL AND RitArrivo>=5 AND RitArrivo<15 AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabR15 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT15 FROM CORSE, TabMaxDate WHERE CORSE.Linea={int(scelta_linea_codice)} AND RitArrivo IS NOT NULL AND RitArrivo>=15 AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabSopp AS (SELECT CORSE.Data as DATE, COUNT(*) AS SOPP FROM CORSE, TabMaxDate WHERE CORSE.Linea={int(scelta_linea_codice)} AND CORSE.Sopp=1 AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabVar AS (SELECT CORSE.Data as DATE, COUNT(*) AS VAR FROM CORSE, TabMaxDate WHERE CORSE.Linea={int(scelta_linea_codice)} AND CORSE.Var=1 AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabDati1 AS (SELECT TGD.DATE AS DATE, NUMTOT, IFNULL(ORARIO,0) AS ORARIO, IFNULL(RIT5,0) AS RIT5, IFNULL(RIT15,0) AS RIT15, IFNULL(SOPP,0) AS SOPP, IFNULL(VAR,0) AS VAR FROM TabGroupDay AS TGD LEFT JOIN TabOr AS TOR ON TGD.DATE=TOR.DATE LEFT JOIN TabR5 AS TR5 ON TGD.DATE=TR5.DATE LEFT JOIN TabR15 AS TR15 ON TGD.DATE=TR15.DATE LEFT JOIN TabSopp as TSP ON TGD.DATE=TSP.DATE LEFT JOIN TabVar as TVR ON TGD.DATE=TVR.DATE) SELECT MIN(DATE) AS DATA_DA, MAX(DATE) AS DATA_A, (SUM(ORARIO)/SUM(NUMTOT))*100 AS PUNTUALITA, SUM(RIT5) AS RIT5, SUM(RIT15) AS RIT15, SUM(SOPP) AS SOPP, SUM(VAR) AS VAR FROM TabDati1;", ttl=0, show_spinner="Caricamento...")
    return puntualita, puntualita_scorsa_sett


def valori_puntualita_iniziali(puntualita):
    data_da = puntualita['DATA_DA'][0]
    data_a = puntualita['DATA_A'][0]
    punt_val = puntualita['PUNTUALITA'][0]
    r5_val = int(puntualita['RIT5'][0])
    r15_val = int(puntualita['RIT15'][0])
    sopp_val = int(puntualita['SOPP'][0])
    var_val = int(puntualita['VAR'][0])
    treni_tot_val = int(puntualita['TRENI_TOT'][0])
    return data_da, data_a, punt_val, r5_val, r15_val, sopp_val, var_val, treni_tot_val


def valori_delta_puntualita(puntualita_scorsa_sett, punt_val, r5_val, r15_val, sopp_val, var_val):
    delta_or_val = punt_val-puntualita_scorsa_sett['PUNTUALITA'][0]
    delta_r5_val = int(r5_val-puntualita_scorsa_sett['RIT5'][0])
    delta_r15_val = int(r15_val-puntualita_scorsa_sett['RIT15'][0])
    delta_sopp_val = int(sopp_val-puntualita_scorsa_sett['SOPP'][0])
    delta_var_val = int(var_val-puntualita_scorsa_sett['VAR'][0])
    return delta_or_val, delta_r5_val, delta_r15_val, delta_sopp_val, delta_var_val





# TAB 2 - RICERCA PER NUMERO TRENO #

def ricerca_per_treno(conn):
    df = conn.query('SELECT NOMELINEA, CodLinea FROM LINEE ORDER BY NOMELINEA;', show_spinner="Caricamento...")
    linee_nome = df['NOMELINEA'].tolist()
    scelta_linea = st.selectbox("**Seleziona la linea da cui scegliere il treno**", linee_nome, index=None, placeholder='Scegli la linea...')

    if scelta_linea != None:
        df2 = conn.query(f"SELECT CodLinea FROM LINEE WHERE NomeLinea='{scelta_linea}';", ttl=0, show_spinner=False)
        scelta_linea_codice = df2['CodLinea'][0]

        elenco_num_treni = conn.query(f'SELECT DISTINCT NumTreno FROM CORSE WHERE Linea={scelta_linea_codice} ORDER BY NumTreno', show_spinner="Caricamento...")
        num_treni_lista = elenco_num_treni['NumTreno'].tolist()
        scelta_treno = st.selectbox("**Seleziona il numero del treno**", num_treni_lista, index=None, placeholder='Scegli il numero del treno...')
        
        if scelta_treno != None:

            # grafico puntualità e medie ritardi in partenza e arrivo #

            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"Puntualità del treno {scelta_treno}")

                    dati_grafico = conn.query(f"with TabTot AS (SELECT COUNT(NumTreno) AS NUMTOT FROM CORSE WHERE NumTreno={scelta_treno}), TabOrario AS (SELECT COUNT(RitArrivo) AS ORARIO FROM CORSE WHERE NumTreno={scelta_treno} AND RitArrivo IS NOT NULL AND RitArrivo<5), TabR5 AS (SELECT COUNT(RitArrivo) AS RIT5 FROM CORSE WHERE NumTreno={scelta_treno} AND RitArrivo IS NOT NULL AND RitArrivo>=5 AND RitArrivo<=14), TabR15 AS (SELECT COUNT(RitArrivo) AS RIT15 FROM CORSE WHERE NumTreno={scelta_treno} AND RitArrivo IS NOT NULL AND RitArrivo>=15), TabSopp AS (SELECT COUNT(Sopp) AS SOPP FROM CORSE WHERE NumTreno={scelta_treno} AND Sopp=1), TabVar AS (SELECT COUNT(Var) AS VAR FROM CORSE WHERE NumTreno={scelta_treno} AND Var=1) SELECT IFNULL((ORARIO/NUMTOT)*100,0) AS PUNT, IFNULL((RIT5/NUMTOT)*100,0) AS RIT5, IFNULL((RIT15/NUMTOT)*100,0) AS RIT15, IFNULL((SOPP/NUMTOT)*100,0) AS SOPP, IFNULL((VAR/NUMTOT)*100,0) AS VAR FROM TabTot AS TT, TabOrario AS TOR, TabR5 AS TR5, TabR15 AS TR15, TabSopp AS TS, TabVar AS TV;", ttl=300, show_spinner="Caricamento...")

                    dati_grafico = dati_grafico.reset_index()
                    dati_grafico = pd.melt(dati_grafico, value_vars=['PUNT', 'RIT5', 'RIT15', 'SOPP', 'VAR'], var_name='LEGENDA', value_name='VALORE')
                    dati_grafico['x'] = 0

                    config = {'displayModeBar': False}
                    fig = px.bar(dati_grafico, x='VALORE', y='x', color='LEGENDA', orientation='h',
                                 color_discrete_map={'PUNT':'#4DAF4A', 'RIT5':'yellow', 'RIT15':'orange', 'SOPP':'red', 'VAR':'purple'}, hover_data={'x':False, 'VALORE':':.2f'})
                    fig.update_layout(margin=dict(t=0, b=0, l=0, r=100), height=200, xaxis_title='Valore percentuale', yaxis_visible=False, xaxis_fixedrange=True, yaxis_fixedrange=True, xaxis_showgrid=True)

                    st.plotly_chart(fig, theme="streamlit", config=config)


                with col2:
                    st.subheader("Statistiche")
                    dati_part = conn.query(f"SELECT avg(ritPart) as MEDIA_RIT_PART FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( ritPart SMALLINT(6) PATH '$.ritPartenza', tipoFermata VARCHAR(1) PATH '$.tipoFermata' ) ) AS tab_fermate WHERE C.NumTreno={scelta_treno} AND tipoFermata='P';", ttl=300, show_spinner="Caricamento...")
                    dati_arr = conn.query(f"SELECT AVG(RitArrivo) AS MEDIA_RIT_ARR FROM CORSE WHERE NumTreno={scelta_treno}", ttl=300, show_spinner="Caricamento...")
                    rit_part = dati_part['MEDIA_RIT_PART'][0]
                    rit_arr = dati_arr['MEDIA_RIT_ARR'][0]
                    if rit_part != None:
                        st.metric(label="Ritardo medio alla partenza", value=f'{round(rit_part,1)} minuti')
                    else:
                        st.metric(label="Ritardo medio alla partenza", value=f'{rit_part} minuti')
                    if rit_arr != None:
                        st.metric(label="Ritardo medio all'arrivo", value=f'{round(rit_arr,1)} minuti')
                    else:
                        st.metric(label="Ritardo medio all'arrivo", value=f'{rit_arr} minuti')

                # PIE DI PAGINA BLOCCO CON GRAFICO E MEDIA RITARDI #
                date = conn.query(f"SELECT MIN(DATA) AS DATAMINIMA, MAX(DATA) AS DATAMASSIMA, COUNT(*) AS NUMTOT FROM CORSE WHERE NumTreno={scelta_treno}", ttl=300, show_spinner="Caricamento...")
                giorno_min = date['DATAMINIMA'][0]
                giorno_max = date['DATAMASSIMA'][0]
                num_corse = date['NUMTOT'][0]
                date_rit_arrivo = conn.query(f"SELECT MIN(DATA) AS DATAMINIMA, MAX(DATA) AS DATAMASSIMA, COUNT(*) AS NUMTOT FROM CORSE WHERE NumTreno={scelta_treno} AND Fermate IS NOT NULL", ttl=300, show_spinner="Caricamento...")
                giorno_min_2 = date_rit_arrivo['DATAMINIMA'][0]

                col3, col4 = st.columns(2)

                with col3:
                    st.markdown(f"su **:blue-background[{num_corse}]** corse totali -  dal **{giorno_min}** al **{giorno_max}**")
                with col4:
                    st.markdown(f"*Il ritardo medio alla partenza è calcolato a partire dal **{giorno_min_2}**")

                # FINE PIE DI PAGINA BLOCCO CON GRAFICO E MEDIA RITARDI #
            
            # BLOCCO STATISTICHE PER STAZIONE
            with st.expander(f"**Statistiche per stazione - treno {scelta_treno}**", icon="🚉"):
                    statistiche_per_stazione(conn, scelta_treno)

            # fine grafici e statistiche #

            df = conn.query(f"SELECT * FROM CORSE WHERE NumTreno={scelta_treno} AND Data>='2025-01-28';", ttl=300, show_spinner="Caricamento...")

            # per visualizzazione dataframe
            df['Sopp'] = df['Sopp'].replace(1, "SI'").replace(0, "NO")
            df['Var'] = df['Var'].replace(1, "SI'").replace(0, "NO")

            # stampa dataframe
            event = st.dataframe(df, on_select="rerun", selection_mode="single-row", column_config={"RitPartenza": None, "OraPartenza": None, "OraArrivo": None, "Fermate": None, "SmartCaring": None, "NumTreno": st.column_config.NumberColumn(format="%f")}, width='stretch', height=300)

            selezione = event.selection.rows
                
            if len(selezione) > 0:
                st.subheader("Fermate")
                fermate = df['Fermate'][selezione[0]]
                if fermate != None:
                    json_fermate = json.loads(fermate)

                    json_fermate = pd.json_normalize(json_fermate)

                    json_fermate['partenzaTeorica'] = pd.to_datetime(json_fermate['partenzaTeorica'], unit='ms', utc=True).dt.tz_convert(tz='Europe/Brussels').dt.strftime('%H:%M:%S')
                    json_fermate['partenzaReale'] = pd.to_datetime(json_fermate['partenzaReale'], unit='ms', utc=True).dt.tz_convert(tz='Europe/Brussels').dt.strftime('%H:%M:%S')
                    json_fermate['arrivoTeorico'] = pd.to_datetime(json_fermate['arrivoTeorico'], unit='ms', utc=True).dt.tz_convert(tz='Europe/Brussels').dt.strftime('%H:%M:%S')
                    json_fermate['arrivoReale'] = pd.to_datetime(json_fermate['arrivoReale'], unit='ms', utc=True).dt.tz_convert(tz='Europe/Brussels').dt.strftime('%H:%M:%S')

                    json_fermate = json_fermate.iloc[:, [0, 8, 9, 10, 2, 3, 4, 5]]

                    json_fermate = json_fermate.rename(columns={"nomeFermata": "Stazione", "partenzaTeorica": "Partenza programmata", "partenzaReale": "Partenza effettiva", "ritPartenza": "Ritardo partenza", "arrivoTeorico": "Arrivo programmato", "arrivoReale": "Arrivo effettivo", "ritArrivo": "Ritardo arrivo", "binEffettivo": "Binario"})
                        
                    st.dataframe(json_fermate, use_container_width = True)
                else:
                    st.warning("Non sono presenti dati relativi alle fermate")


                #st.subheader("Smart caring")
                #smart_caring = df['SmartCaring'][selezione[0]]
                #if smart_caring != None:
                #    json_smart_caring = json.loads(smart_caring)

                #    for avviso in json_smart_caring:
                #        with st.container(border=True):
                #            st.markdown(f"**{converti_data_ora(avviso['oraAvviso'])}**\n")
                #            st.markdown(f"{avviso['testoAvviso']}")

                #else:
                #    st.info("Non sono presenti dati relativi allo smart caring")

            else:
                st.info("Seleziona un treno dalla tabella per visualizzare i dati sul percorso, cliccando sul margine sinistro della riga", icon="ℹ")


# funzione per blocco statistiche aggiuntive per stazione #
def statistiche_per_stazione(conn, scelta_treno):

    stazioni = conn.query(f"SELECT tab_fermate.nomeFermata FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritArr SMALLINT(6) PATH '$.ritArrivo', ritPart SMALLINT(6) PATH '$.ritPartenza' ) ) AS tab_fermate WHERE C.Data=(SELECT MAX(Data) FROM CORSE WHERE NumTreno={scelta_treno} AND Fermate IS NOT NULL) AND C.NumTreno={scelta_treno};", ttl=300, show_spinner="Caricamento...")
    stazioni_lista = stazioni['nomeFermata'].tolist()
    scelta_stazione = st.selectbox("**Seleziona una stazione**", stazioni_lista, index=None, placeholder='Scegli una stazione...')

    date = conn.query(f"SELECT MIN(Data) AS DATAMIN, MAX(Data) AS DATAMAX FROM CORSE WHERE NumTreno={scelta_treno} AND Fermate IS NOT NULL", ttl=300, show_spinner="Caricamento...")
    data_min = date['DATAMIN'][0]
    data_max = date['DATAMAX'][0]
    intervallo_date = st.date_input("**Scegli l'intervallo di date per le statistiche**",value=(data_min, data_max),min_value=data_min,max_value=data_max)
                
    if len(intervallo_date) != 1:
                
        giorno_1 = intervallo_date[0]
        giorno_2 = intervallo_date[1]

                    
        if scelta_stazione != None:
            
            dati_box_plot = conn.query(f"SELECT C.Data, tab_fermate.nomeFermata, ritArr, ritPart FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritArr SMALLINT(6) PATH '$.ritArrivo', ritPart SMALLINT(6) PATH '$.ritPartenza' ) ) AS tab_fermate WHERE nomeFermata='{scelta_stazione}' AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND C.NumTreno={scelta_treno};", ttl=300, show_spinner="Caricamento...")

            if dati_box_plot['ritArr'].isnull().all():
                scelta_arr_part = st.radio("**Scegli se visualizzare il ritardo di arrivo o di partenza**", options=['Arrivo', 'Partenza'], index=1, disabled=True, horizontal=True)
            elif dati_box_plot['ritPart'].isnull().all():
                scelta_arr_part = st.radio("**Scegli se visualizzare il ritardo di arrivo o di partenza**", options=['Arrivo', 'Partenza'], index=0, disabled=True, horizontal=True)
            else:
                scelta_arr_part = st.radio("**Scegli se visualizzare il ritardo di arrivo o di partenza**", options=['Arrivo', 'Partenza'], disabled=False, horizontal=True)
                    
            if scelta_arr_part == 'Arrivo':
                tipo_rit = 'ritArr'
            elif scelta_arr_part == 'Partenza':
                tipo_rit = 'ritPart'
                    
        col1, col2, col3 = st.columns(3, gap="medium")
    
        with col1:
            if scelta_stazione != None:

                st.markdown("**Grafico:**")

                config = {'displayModeBar': False}
                fig_box = px.box(dati_box_plot, y=tipo_rit, points='all')
                fig_box.update_traces(quartilemethod="linear", boxmean=True)
                # fig_box.update_layout(yaxis_tickformat="d")
                fig_box.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=400, xaxis_title=f"{scelta_treno}", yaxis_visible=True, xaxis_fixedrange=True, yaxis_fixedrange=True, xaxis_showgrid=False)

                st.plotly_chart(fig_box, theme="streamlit", config=config)

        with col2:
            if scelta_stazione != None:

                punt_df = conn.query(f"with TabTotArrivo AS (SELECT count(ritArr) AS TOTARR FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritArr SMALLINT(6) PATH '$.ritArrivo' ) ) AS tab_fermate WHERE nomeFermata='{scelta_stazione}' AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND C.NumTreno={scelta_treno}), TabTotPartenza AS (SELECT count(ritPart) AS TOTPART FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritPart SMALLINT(6) PATH '$.ritPartenza' ) ) AS tab_fermate WHERE nomeFermata='{scelta_stazione}' AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND C.NumTreno={scelta_treno}), TabPuntArrivo AS (SELECT count(ritArr) AS ORARIOARR FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritArr SMALLINT(6) PATH '$.ritArrivo' ) ) AS tab_fermate WHERE nomeFermata='{scelta_stazione}' AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND C.NumTreno={scelta_treno} AND ritArr<5), TabPuntPartenza AS (SELECT count(ritPart) AS ORARIOPART FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritPart SMALLINT(6) PATH '$.ritPartenza' ) ) AS tab_fermate WHERE nomeFermata='{scelta_stazione}' AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND C.NumTreno={scelta_treno} AND ritPart<5) SELECT IFNULL((ORARIOARR/TOTARR)*100,0) AS PUNTARRIVO, IFNULL((ORARIOPART/TOTPART)*100,0) AS PUNTPARTENZA FROM TabTotArrivo, TabTotPartenza, TabPuntArrivo, TabPuntPartenza;", ttl=300, show_spinner="Caricamento...")
                if scelta_arr_part == 'Arrivo':
                    punt = punt_df['PUNTARRIVO'][0]
                elif scelta_arr_part == 'Partenza':
                    punt = punt_df['PUNTPARTENZA'][0]
                avg = dati_box_plot[tipo_rit].mean()
                std = dati_box_plot[tipo_rit].std()
                med = dati_box_plot[tipo_rit].median()
                q1 = dati_box_plot[tipo_rit].quantile(q=0.25, interpolation='hazen') 
                q3 = dati_box_plot[tipo_rit].quantile(q=0.75, interpolation='hazen')

                st.markdown("**Statistiche aggiuntive:**")

                col4, col5 = st.columns(2)
                col4.metric("Puntualità su treni effettuati", f"{round(punt,2)}%")
                col5.metric("Media", f"{round(avg,1)} min")
                            
                col6, col7 = st.columns(2)
                col6.metric("Mediana", f"{med} min")
                col7.metric("Deviazione Standard", f"{round(std,1)} min")
                            
                col8, col9 = st.columns(2)
                col8.metric("1° quartile", f"{q1} min")
                col9.metric("3° quartile", f"{q3} min")

        with col3:
            if scelta_stazione != None:
                st.markdown("**Dettaglio per singoli giorni:**")
                st.dataframe(dati_box_plot, column_config={"nomeFermata": None}, height=400, width='stretch')

    else:
        st.info("Seleziona un intervallo di date per visualizzare le statistiche", icon="ℹ")





# TAB 3 - MAPPA #

def visualizza_mappa_stazioni(conn):
    df2 = conn.query('with TabRitStazioni AS (SELECT T.StazArrivo, AVG(C.RitArrivo) AS MEDIARIT FROM CORSE AS C, TRENI AS T WHERE C.NumTreno = T.NumTreno GROUP BY T.StazArrivo) SELECT StazArrivo, NomeStazione, MEDIARIT, LAT, LON FROM TabRitStazioni AS TR, STAZIONI AS S WHERE TR.StazArrivo = S.CodStazione;', ttl=0, show_spinner="Caricamento...")
    df2 = df2.round({'MEDIARIT':2})

    # layer mappa
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df2,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=6,
        radius_min_pixels=1,
        radius_max_pixels=100,
        line_width_min_pixels=1,
        get_position='[LON, LAT]',
        get_radius=300,
        get_fill_color=[255,140,0],
        get_line_color=[0,0,0],)
        
    view_state = pdk.ViewState(latitude=45.37233, longitude=8.12934, zoom=7, bearing=0, pitch=None)

    st.pydeck_chart(pdk.Deck(initial_view_state=view_state, layers=[layer], tooltip={"text": "Stazione di:\n{NomeStazione}\nMedia ritardi:\n{MEDIARIT} minuti"}), height=700)
